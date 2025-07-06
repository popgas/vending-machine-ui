import base64
import os
from dataclasses import dataclass, replace
from typing import Optional
import platform

import cv2

from domains.enums.machine_doors import VendingMachinePins
from domains.enums.order_product_selected import OrderProductSelected
from typing import TypedDict, Dict

class PriceInfo(TypedDict):
    gas_price: float
    container_price: int

@dataclass(frozen=True)
class NewOrderIntent:
    productSelected: OrderProductSelected
    productPrice: float
    selectedPaymentMethodPrice: float
    stockCount: int
    pricesByPaymentMethod: Optional[Dict[str, PriceInfo]] = None,
    paymentMethodId: Optional[int] = None
    correlationId: Optional[str] = None
    placedContainerPhoto: Optional[str] = None
    purchasedContainerPhoto: Optional[str] = None

    def copy_with(
        self,
        paymentMethodId: Optional[int] = None,
        selectedPaymentMethodPrice: Optional[float] = None,
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
            selectedPaymentMethodPrice=selectedPaymentMethodPrice if selectedPaymentMethodPrice is not None else self.selectedPaymentMethodPrice,
            stockCount=self.stockCount,
            pricesByPaymentMethod=self.pricesByPaymentMethod,
            paymentMethodId=paymentMethodId if paymentMethodId is not None else self.paymentMethodId,
            correlationId=correlationId if correlationId is not None else self.correlationId,
            placedContainerPhoto=placedContainerPhoto if placedContainerPhoto is not None else self.placedContainerPhoto,
            purchasedContainerPhoto=purchasedContainerPhoto if purchasedContainerPhoto is not None else self.purchasedContainerPhoto
        )

    def get_full_container_open_door_pin(self):
        if self.stockCount == 27:
            return VendingMachinePins.openDoor2

        return self.get_refill_open_door_pin()

    def get_full_container_close_door_pin(self):
        if self.stockCount == 27:
            return VendingMachinePins.closeDoor2

        return self.get_refill_close_door_pin()

    def get_refill_open_door_pin(self) -> int:
        """
        Returns the pin number for opening a door based on the stock count.
        """
        if self.__use_first_door():
            return VendingMachinePins.openDoor1
        elif self.__use_second_doors():
            return VendingMachinePins.openDoor2
        else:
            return VendingMachinePins.openDoor3

    def get_refill_close_door_pin(self) -> int:
        """
        Returns the pin number for closing a door based on the stock count.
        """
        if self.__use_first_door():
            return VendingMachinePins.closeDoor1
        elif self.__use_second_doors():
            return VendingMachinePins.closeDoor2
        else:
            return VendingMachinePins.closeDoor3

    def get_camera(self) -> int | str:
        if platform.system() == 'Darwin':
            return 0

        if self.__use_first_door():
            return os.environ['CAMERA_1']
        elif self.__use_second_doors():
            return os.environ['CAMERA_2']
        else:
            return os.environ['CAMERA_3']

    def get_camera_describer(self) -> str:
        if self.__use_first_door():
            return 'CAMERA_1'
        elif self.__use_second_doors():
            return 'CAMERA_2'
        else:
            return 'CAMERA_3'

    def get_placed_container_photo_as_base64(self) -> Optional[str]:
        if self.placedContainerPhoto is not None:
            retval, buffer = cv2.imencode('.jpg', self.placedContainerPhoto)
            return base64.b64encode(buffer).decode("utf-8")

    def get_purchased_container_photo_as_base64(self) -> Optional[str]:
        if self.purchasedContainerPhoto is not None:
            retval, buffer = cv2.imencode('.jpg', self.purchasedContainerPhoto)
            return base64.b64encode(buffer).decode("utf-8")

    def __use_first_door(self):
        return self.stockCount >= 27

    def __use_second_doors(self):
        return self.stockCount >= 14
