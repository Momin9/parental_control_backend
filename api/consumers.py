import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChildLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "child_tracking"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_location",
                "latitude": data["latitude"],
                "longitude": data["longitude"],
            },
        )

    async def send_location(self, event):
        await self.send(text_data=json.dumps({
            "latitude": event["latitude"],
            "longitude": event["longitude"],
        }))
