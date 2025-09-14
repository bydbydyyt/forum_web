import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import UserStatus, Message, ChatRoom, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # 加入聊天室组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # 更新用户在线状态
        await self.update_user_status(True)
        
        await self.accept()

    async def disconnect(self, close_code):
        # 离开聊天室组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # 更新用户离线状态
        await self.update_user_status(False)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'chat_message':
            message = text_data_json['message']
            sender = self.scope['user']
            
            # 保存消息到数据库
            room = await self.get_room()
            saved_message = await self.save_message(room, sender, message)
            
            # 发送消息到聊天室组
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender.username,
                    'created_at': saved_message.created_at.isoformat(),
                    'is_sent': True
                }
            )
            
            # 创建消息通知
            await self.create_message_notification(room, sender, message)
            
        elif message_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing',
                    'user': self.scope['user'].username,
                    'is_typing': text_data_json['is_typing']
                }
            )

    async def chat_message(self, event):
        # 判断当前用户是否为消息发送者
        current_user = self.scope['user']
        is_sent = current_user.username == event['sender']
        
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'created_at': event.get('created_at'),
            'is_sent': is_sent
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))

    @database_sync_to_async
    def update_user_status(self, is_online):
        user = self.scope['user']
        status, created = UserStatus.objects.get_or_create(user=user)
        status.is_online = is_online
        status.save()

    @database_sync_to_async
    def get_room(self):
        room, created = ChatRoom.objects.get_or_create(name=self.room_name)
        # 如果是新创建的聊天室，添加当前用户为参与者
        if created:
            room.participants.add(self.scope['user'])
        # 确保当前用户在聊天室的参与者列表中
        elif not room.participants.filter(id=self.scope['user'].id).exists():
            room.participants.add(self.scope['user'])
        return room

    @database_sync_to_async
    def save_message(self, room, sender, content):
        return Message.objects.create(
            room=room,
            sender=sender,
            content=content,
            message_type='text'
        )

    @database_sync_to_async
    def create_message_notification(self, room, sender, message):
        # 获取聊天室中的其他用户
        other_users = room.participants.exclude(id=sender.id)
        
        # 为每个其他用户创建通知
        for user in other_users:
            Notification.objects.create(
                user=user,
                message=f'{sender.username} 发送了新消息: {message[:50]}...',
                notification_type='message',
                related_user=sender
            )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
            
        self.group_name = f'notifications_{self.user.id}'
        
        # 加入用户通知组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # 离开用户通知组
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'notification_read':
            notification_id = text_data_json.get('notification_id')
            await self.mark_notification_read(notification_id)

    async def new_notification(self, event):
        # 发送新通知到客户端
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass


class FriendsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
            
        self.group_name = f'friends_{self.user.id}'
        
        # 加入用户好友组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # 离开用户好友组
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'friend_request':
            target_username = text_data_json.get('target_username')
            await self.send_friend_request(target_username)

    async def friend_status_update(self, event):
        # 发送好友状态更新到客户端
        await self.send(text_data=json.dumps({
            'type': 'friend_status_update',
            'friend': event['friend'],
            'is_online': event['is_online']
        }))

    async def new_friend_request(self, event):
        # 发送新好友请求到客户端
        await self.send(text_data=json.dumps({
            'type': 'new_friend_request',
            'requester': event['requester']
        }))

    @database_sync_to_async
    def send_friend_request(self, target_username):
        try:
            target_user = User.objects.get(username=target_username)
            # 这里可以添加发送好友请求的逻辑
            pass
        except User.DoesNotExist:
            pass