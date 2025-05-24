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
            await self.save_message(room, sender, message)
            
            # 发送消息到聊天室组
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender.username
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
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender']
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
        return ChatRoom.objects.get(name=self.room_name)

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