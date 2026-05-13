import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock Tkinter classes
class MockWidget:
    def __init__(self, master=None, *args, **kwargs):
        pass
    def __getitem__(self, key):
        return MagicMock()
    def __setitem__(self, key, value):
        pass
    def __getattr__(self, name):
        return MagicMock()
    def __call__(self, *args, **kwargs):
        return MagicMock()
    def winfo_children(self):
        return []

mock_tk = MagicMock()
mock_tk.Tk = MockWidget
mock_tk.Frame = MockWidget
mock_tk.Toplevel = MockWidget
mock_tk.Canvas = MockWidget
mock_tk.Label = MockWidget
mock_tk.Button = MockWidget

sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.font'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()

# Mock dependencies used in index.py/application.py or screens
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['qrcode'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['ably'] = MagicMock() # used by card_machine

from application import Application

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.app = Application(routes={})
        # Mock container
        self.app.container = MagicMock()

    def test_push_and_back(self):
        # Define a mock screen class that behaves like a widget
        class MockScreen:
            def __init__(self, app, props=None):
                self.app = app
                self.props = props
                self.place = MagicMock()
                self.tkraise = MagicMock()
                self.destroy = MagicMock()
                self.pack = MagicMock()
                
            def build(self): pass
            
        # Re-init app with routes
        self.app = Application(routes={
            'screen1': MockScreen,
            'screen2': MockScreen
        })
        # Mock container again
        self.app.container = MagicMock()
        
        # Push
        self.app.push('screen1', {'data': 1})
        
        self.assertEqual(len(self.app.nav_stack), 1)
        self.assertIsInstance(self.app.nav_stack[0], MockScreen)
        self.assertEqual(self.app.nav_stack[0].props, {'data': 1})
        
        # Push another (must be different name to avoid deduplication)
        self.app.push('screen2', {'data': 2})
        self.assertEqual(len(self.app.nav_stack), 2)
        
        # Pop
        self.app.pop()
        self.assertEqual(len(self.app.nav_stack), 1) 
        self.assertEqual(self.app.nav_stack[0].props, {'data': 1})
        
    def test_reset(self):
        class MockScreen:
            def __init__(self, app, props=None):
                self.destroy = MagicMock()
                self.place = MagicMock()
                self.tkraise = MagicMock()
        
        # Re-init
        self.app = Application(routes={'s': MockScreen, 's2': MockScreen})
        self.app.container = MagicMock()
        
        self.app.push('s')
        self.app.push('s2') 
        
        self.assertEqual(len(self.app.nav_stack), 2)
        
    def test_edge_cases(self):
        # 1. Duplicate Push
        mock_screen = MagicMock()
        self.app.routes = {'s': lambda app, *args: mock_screen}
        
        self.app.push('s')
        self.assertEqual(len(self.app.nav_stack), 1)
        
        # Try pushing same again
        self.app.push('s')
        self.assertEqual(len(self.app.nav_stack), 1) # Should not increase
        
        # 2. Unknown Route
        self.app.push('unknown')
        self.assertEqual(len(self.app.nav_stack), 1) # Should not change
        
        # 3. Pop with 1 item
        self.app.pop()
        self.assertEqual(len(self.app.nav_stack), 1) # Cannot pop last item
        
        # 4. Background methods (just coverage)
        self.app.show_bg()
        self.app.hide_bg()

    def test_lifecycle_hooks(self):
        # Mock widgets with dispose / on_route_popped
        widget1 = MagicMock()
        widget1.dispose = MagicMock()
        widget1.on_route_popped = MagicMock()
        
        widget2 = MagicMock()
        widget2.on_route_mounted = MagicMock()
        
        self.app.routes = {
            'w1': lambda app, *args: widget1,
            'w2': lambda app, *args: widget2
        }
        
        self.app.push('w1')
        self.app.push('w2')
        widget2.on_route_mounted.assert_called()
        
        self.app.pop()
        # widget2 popped -> dispose called?
        # Pop logic:
        # current = pop()
        # if has dispose: dispose()
        # current.destroy()
        # previous = stack[-1]
        # if has on_route_popped: on_route_popped()
        
        # widget2 was popped (current)
        if hasattr(widget2, 'dispose'):
             widget2.dispose.assert_called()
             
        # widget1 is now top (previous)
        widget1.on_route_popped.assert_called()

    def test_off_all(self):
        mock_s = MagicMock()
        self.app.routes = {'s': lambda app, *args: mock_s}
        self.app.push('s')
        self.app.push('s') # duplicate check prevents this? No, same instance, different push?
        # Duplicate check checks name. So we need distinct names.
        self.app.routes['s2'] = lambda app, *args: mock_s
        self.app.push('s2')
        
        self.assertEqual(len(self.app.nav_stack), 2)
        
        self.app.off_all('s')
        
        self.assertEqual(len(self.app.nav_stack), 1)
        self.assertEqual(self.app.nav_stack_names[0], 's')

if __name__ == '__main__':
    unittest.main()
