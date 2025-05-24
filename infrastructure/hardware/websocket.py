import asyncio
import os

from ably import AblyRealtime
from ably.types.message import Message

from domains.enums.machine_doors import VendingMachinePins
from infrastructure.hardware.camera import CameraWorker
from infrastructure.hardware.gpio import GpioWorker


class Websocket:
    def __init__(self):
        self.channel_name = f'vending_machine_{os.environ['VENDING_MACHINE_ID']}'
        self.command_name = f'{self.channel_name}:commands'
        self.result_name = f'{self.channel_name}::results'
        print(self.command_name)
        self.channel_command_handler = None
        self.channel_result_handler = None

    @staticmethod
    async def configure():
        websocket = Websocket()
        await websocket.connect()
        await asyncio.Event().wait()

    async def connect(self):
        ably = AblyRealtime(os.environ['ABLY_KEY'])

        await ably.connection.once_async('connected')

        print("connected")

        channel = ably.channels.get(self.command_name)
        # self.channel_result_handler = ably.channels.get(self.result_name)
        await channel.subscribe(self.command_handler)

    async def command_handler(self, event: Message):
        print(f'__command_handler: {event}')

        match event.name:
            case 'cameras:take_photos':
                await self.__take_photos(event)
            case 'doors:open':
                await self.__open_doors(event)
            case 'doors:close':
                await self.__close_doors(event)

    async def __take_photos(self, event: Message):
        GpioWorker.close_all_doors()

        photos = CameraWorker.take_photo_from_all_cameras()

        await self.channel_result_handler.publish(event.name, {
            'photos': photos
        })

    async def __open_doors(self, event: Message):
        match event.data['door_number']:
            case 1:
                GpioWorker.activate(VendingMachinePins.openDoor1)
            case 2:
                GpioWorker.activate(VendingMachinePins.openDoor2)
            case 3:
                GpioWorker.activate(VendingMachinePins.openDoor3)

        await self.channel_result_handler.publish(event['name'])

    async def __close_doors(self, event: Message):
        match event.data['door_number']:
            case 1:
                GpioWorker.activate(VendingMachinePins.closeDoor1)
            case 2:
                GpioWorker.activate(VendingMachinePins.closeDoor2)
            case 3:
                GpioWorker.activate(VendingMachinePins.closeDoor3)

        await self.channel_result_handler.publish(event['name'])
