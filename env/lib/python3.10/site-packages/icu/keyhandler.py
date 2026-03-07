from itertools import cycle
from threading import Timer

from collections import defaultdict
from . import event
from .event import Event, EventCallback

from .component import BaseComponent
from .constants import EVENT_LABEL_KEY
from .generator import EventGenerator

MAX_KEY_CODES = 120

HOLD_FREQUENCY = 20 # 50 events per second TODO make configurable
SINGLE_PRESS_MAX_SECONDS = 0.05 #is this ok for debouncing?

# TODO define commonly used key codes  (Left, Right, Up, Down, A, S, W, D) + Joystick??

#consider using os.system('xset r off') # debouncing...

class KeyHandler(EventCallback): 
    """ 
        A KeyHandler records keyboard key press and release events. 
    """
    
    def __init__(self, root):
        super(KeyHandler, self).__init__()

        EventCallback.register(self, self.__class__.__name__)

        root.bind_all('<KeyPress>', self.__db_press)
        root.bind_all('<KeyRelease>', self.__db_release)

        self.keys = defaultdict(lambda: False)
        self.timers = defaultdict(lambda: None)
        self.holds = defaultdict(lambda: None)
    
    def __db_release_timer(self, event): #debounce
        self.keys[event.keysym] = False
        self.release(event)

    def __db_press(self, event): #debounce
        timer = self.timers[event.keysym]
        if timer is not None:
            timer.cancel()
            del self.timers[event.keysym]
            
        if not self.keys[event.keysym]:
            self.keys[event.keysym] = True
            self.press(event)

    def __db_release(self, event): #debounce
        timer = Timer(SINGLE_PRESS_MAX_SECONDS, self.__db_release_timer, [event])
        self.timers[event.keysym] = timer
        timer.start()

    def press(self, event):
        """ Called when a keyboard key is pressed.
        Args:
            event (keyevent): A key event, should contain the attribute keysym (a unique identifier for the key).
        """
        #print("press", event)
        sym = "<{0}>".format(event.keysym)
        for v in BaseComponent.bound(sym).values():
            self.source(v.name, label=EVENT_LABEL_KEY, key=event.keysym, keycode=event.keycode, action='press')
            self.hold(v.name, label=EVENT_LABEL_KEY, key=event.keysym, keycode=event.keycode, action='hold')

    def release(self, event):
        """ Called when a keyboard key is released.
        Args:
            event (keyevent): A key event, should contain the attribute keysym (a unique identifier for the key).
        """
        #print("release", event)
        sym = "<{0}>".format(event.keysym)
        for v in BaseComponent.bound(sym).values():
            self.holds[event.keysym].released() #stop generating hold events
            self.source(v.name, label=EVENT_LABEL_KEY, key=event.keysym, keycode=event.keycode, action='release')

    def isPressed(self, key):
        """ is the given key currently being pressed?
        
        Args:
            key ( -- ): the unique identifier associated with the key (see press, release) 
        
        Returns:
            bool: True if the key is currently pressed, False otherwise.
        """
        return self.keys[key]

    def hold(self, sink, key, label=EVENT_LABEL_KEY, **data):
        """ periodically trigger key events to the given component

        Args:
            component (str): sink name to receive key events
            key (str): key that is to be sent
            data (str): any additional event data to be sent...

        Returns:
            KeyHoldGenerator: event generator.
        """
        generator = KeyHoldGenerator(self, sink, key=key, label=label, **data)
        event.event_scheduler.schedule(generator, sleep=cycle([1000/HOLD_FREQUENCY]))
        self.holds[key] = generator

class KeyHoldGenerator(EventGenerator):
    """ 
        Periodically generally key events when a key is being held down.
    """
    def __init__(self, keyhandler, component, **data):
        super(KeyHoldGenerator, self).__init__()
        self.keyhandler = keyhandler
        self.component = component
        self.data = data #key, keycode, label etc
        self.key = data['key']
        self.stop = False

    def __next__(self):
        if not self.stop:
            return Event(KeyHandler.__name__, self.component, **self.data)
        else:
            raise StopIteration()

    def released(self):
        self.stop = True

class JoyStickHandler:

    def __init__(self, root):
        raise NotImplementedError("TODO are we using a joystick!?")

    def press(self, event):
        pass #TODO

    def release(self, event):
        pass #TODO

    def isPressed(self, key):
        pass #TODO