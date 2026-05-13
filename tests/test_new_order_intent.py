import unittest
from unittest.mock import patch, MagicMock
import os
import platform
from domains.enums.machine_doors import VendingMachinePins
from domains.enums.order_product_selected import OrderProductSelected
from presentation.abstractions.new_order_intent import NewOrderIntent

class TestNewOrderIntent(unittest.TestCase):
    def setUp(self):
        self.base_intent = NewOrderIntent(
            productSelected=OrderProductSelected.gasWithContainer,
            productPrice=100.0,
            stockCount=30, # Default to first door (> 27)
        )

    def test_copy_with(self):
        # Test updating single field
        new_intent = self.base_intent.copy_with(paymentMethodId=1)
        self.assertEqual(new_intent.paymentMethodId, 1)
        self.assertEqual(new_intent.productPrice, 100.0)

        # Test updating multiple fields
        new_intent = self.base_intent.copy_with(
            correlationId="123",
            placedContainerPhoto="photo1",
            purchasedContainerPhoto="photo2",
            selectedPaymentMethodPrice=90.0
        )
        self.assertEqual(new_intent.correlationId, "123")
        self.assertEqual(new_intent.placedContainerPhoto, "photo1")
        self.assertEqual(new_intent.purchasedContainerPhoto, "photo2")
        self.assertEqual(new_intent.selectedPaymentMethodPrice, 90.0)

        # Test no updates
        same_intent = self.base_intent.copy_with()
        self.assertEqual(same_intent.productPrice, self.base_intent.productPrice)

    def test_door_logic_first_door(self):
        # stockCount >= 27 -> First Door
        intent = NewOrderIntent(OrderProductSelected.onlyGasRefill, 100.0, stockCount=27)
        self.assertEqual(intent.get_refill_open_door_pin(), VendingMachinePins.openDoor1)
        self.assertEqual(intent.get_refill_close_door_pin(), VendingMachinePins.closeDoor1)
        
        # Logic for full container is same as refill unless explicit override?
        # The class has get_full_container_open_door_pin which has specific logic for 27
        self.assertEqual(intent.get_full_container_open_door_pin(), VendingMachinePins.openDoor2) # wait, inspecting code logic
        self.assertEqual(intent.get_full_container_close_door_pin(), VendingMachinePins.closeDoor2)

    def test_door_logic_second_door(self):
        # 14 <= stockCount < 27 -> Second Door
        intent = NewOrderIntent(OrderProductSelected.onlyGasRefill, 100.0, stockCount=14)
        self.assertEqual(intent.get_refill_open_door_pin(), VendingMachinePins.openDoor2)
        self.assertEqual(intent.get_refill_close_door_pin(), VendingMachinePins.closeDoor2)
        
        # For full container
        # get_full_container calls get_refill if stockCount != 27
        self.assertEqual(intent.get_full_container_open_door_pin(), VendingMachinePins.openDoor2)

    def test_door_logic_third_door(self):
        # stockCount < 14 -> Third Door
        intent = NewOrderIntent(OrderProductSelected.onlyGasRefill, 100.0, stockCount=13)
        self.assertEqual(intent.get_refill_open_door_pin(), VendingMachinePins.openDoor3)
        self.assertEqual(intent.get_refill_close_door_pin(), VendingMachinePins.closeDoor3)

    @patch('platform.system')
    def test_get_camera_mac(self, mock_system):
        mock_system.return_value = 'Darwin'
        self.assertEqual(self.base_intent.get_camera(), 0)

    @patch('platform.system')
    @patch.dict(os.environ, {'CAMERA_1': 'cam1', 'CAMERA_2': 'cam2', 'CAMERA_3': 'cam3'})
    def test_get_camera_linux(self, mock_system):
        mock_system.return_value = 'Linux'
        
        # First Door
        i1 = NewOrderIntent(OrderProductSelected.onlyGasRefill, 100.0, stockCount=30)
        self.assertEqual(i1.get_camera(), 'cam1')
        self.assertEqual(i1.get_camera_describer(), 'CAMERA_1')

        # Second Door
        i2 = NewOrderIntent(OrderProductSelected.onlyGasRefill, 100.0, stockCount=20)
        self.assertEqual(i2.get_camera(), 'cam2')
        self.assertEqual(i2.get_camera_describer(), 'CAMERA_2')
        
        # Third Door
        i3 = NewOrderIntent(OrderProductSelected.onlyGasRefill, 100.0, stockCount=5)
        self.assertEqual(i3.get_camera(), 'cam3')
        self.assertEqual(i3.get_camera_describer(), 'CAMERA_3')

    @patch('cv2.imencode')
    @patch('base64.b64encode')
    def test_photos_as_base64(self, mock_b64, mock_imencode):
        mock_imencode.return_value = (True, b'imgdata')
        mock_b64.return_value = b'b64data'
        
        intent = self.base_intent.copy_with(
            placedContainerPhoto=MagicMock(),
            purchasedContainerPhoto=MagicMock()
        )
        
        self.assertEqual(intent.get_placed_container_photo_as_base64(), "b64data")
        self.assertEqual(intent.get_purchased_container_photo_as_base64(), "b64data")
        
        # Test None
        empty_intent = self.base_intent
        self.assertIsNone(empty_intent.get_placed_container_photo_as_base64())
        self.assertIsNone(empty_intent.get_purchased_container_photo_as_base64())

if __name__ == '__main__':
    unittest.main()
