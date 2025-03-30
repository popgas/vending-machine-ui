import base64
from dataclasses import dataclass, replace
from typing import Optional
import platform

import cv2

from domains.enums.machine_doors import VendingMachinePins
from domains.enums.order_product_selected import OrderProductSelected


@dataclass(frozen=True)
class NewOrderIntent:
    productSelected: OrderProductSelected
    productPrice: float
    stockCount: int
    paymentMethodId: Optional[int] = None
    correlationId: Optional[str] = None
    placedContainerPhoto: Optional[str] = None
    purchasedContainerPhoto: Optional[str] = None

    def copy_with(
        self,
        paymentMethodId: Optional[int] = None,
        correlationId: Optional[str] = None,
        placedContainerPhoto: Optional[str] = None,
        purchasedContainerPhoto: Optional[str] = None,
    ) -> 'NewOrderIntent':
        """
        Returns a new instance of NewOrderIntent with updated values.
        If an argument is None, the original value is retained.
        """
        return NewOrderIntent(
            productSelected=self.productSelected,
            productPrice=self.productPrice,
            stockCount=self.stockCount,
            paymentMethodId=paymentMethodId if paymentMethodId is not None else self.paymentMethodId,
            correlationId=correlationId if correlationId is not None else self.correlationId,
            placedContainerPhoto=placedContainerPhoto if placedContainerPhoto is not None else self.placedContainerPhoto,
            purchasedContainerPhoto=purchasedContainerPhoto if purchasedContainerPhoto is not None else self.purchasedContainerPhoto
        )

    def get_open_door_pin(self) -> int:
        """
        Returns the pin number for opening a door based on the stock count.
        """
        if self.stockCount >= 28:
            return VendingMachinePins.openDoor1
        elif self.stockCount >= 15:
            return VendingMachinePins.openDoor2
        else:
            return VendingMachinePins.openDoor3

    def get_close_door_pin(self) -> int:
        """
        Returns the pin number for closing a door based on the stock count.
        """
        if self.stockCount >= 28:
            return VendingMachinePins.closeDoor1
        elif self.stockCount >= 15:
            return VendingMachinePins.closeDoor2
        else:
            return VendingMachinePins.closeDoor3

    def get_camera(self) -> int | str:
        if platform.system() == 'Darwin':
            return 0

        if self.stockCount >= 28:
            return '/dev/video0'
        elif self.stockCount >= 15:
            return '/dev/video4'
        else:
            return '/dev/video2'

    def get_placed_container_photo_as_base64(self) -> Optional[str]:
        if self.placedContainerPhoto is not None:
            retval, buffer = cv2.imencode('.jpg', self.placedContainerPhoto)
            return base64.b64encode(buffer).decode("utf-8")

    def get_purchased_container_photo_as_base64(self) -> Optional[str]:
        if self.purchasedContainerPhoto is not None:
            retval, buffer = cv2.imencode('.jpg', self.purchasedContainerPhoto)
            return base64.b64encode(buffer).decode("utf-8")

