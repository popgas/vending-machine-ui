import asyncio

from ably import AblyRealtime
from ably.types.message import Message

from domains.enums.machine_doors import VendingMachinePins
from infrastructure.environment import get_env
from infrastructure.hardware.camera import CameraWorker
from infrastructure.hardware.gpio import GpioWorker
from infrastructure.observability.logger import Logger


class Websocket:
    def __init__(self):
        vm_id = get_env('VENDING_MACHINE_ID', 'dev-vm-01')
        self.channel_name = f'vending_machine_{vm_id}'
        self.command_name = f'{self.channel_name}:commands'
        self.result_name = f'{self.channel_name}::results'
        print(self.command_name)
        self.channel_command_handler = None
        self.channel_result_handler = None

    @staticmethod
    async def configure():
        ably_key = get_env('ABLY_KEY')
        if not ably_key:
            Logger.get_logger().warning("ABLY_KEY ausente; websocket skipped")
            return

        try:
            websocket = Websocket()
            await websocket.connect(ably_key)
            await asyncio.Event().wait()
        except Exception as e:
            Logger.get_logger().warning(f"websocket configure skipped: {e}")

    async def connect(self, ably_key: str):
        ably = AblyRealtime(ably_key)

        await ably.connection.once_async('connected')

        print("connected")

        channel = ably.channels.get(self.command_name)
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
