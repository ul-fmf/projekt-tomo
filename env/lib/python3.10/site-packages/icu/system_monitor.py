import tkinter as tk
import random
import copy
import time
from types import SimpleNamespace

from . import panel



from .constants import BACKGROUND_COLOUR, OUTLINE_WIDTH, OUTLINE_COLOUR, COLOUR_LIGHT_BLUE, COLOUR_BLUE
from .constants import SYSTEM_MONITOR_SCALE_POSITIONS, COLOUR_GREEN, COLOUR_RED
from .constants import WARNING_OUTLINE_COLOUR, WARNING_OUTLINE_WIDTH
from .constants import EVENT_LABEL_CLICK, EVENT_LABEL_KEY


#from .constants import WARNING_LIGHT_MIN_HEIGHT, WARNING_LIGHT_MIN_WIDTH

from .event import Event, EventCallback, get_event_sinks

from .component import Component, CanvasWidget, SimpleComponent, BoxComponent, LineComponent
from .highlight import Highlight

#TODO refactor (constants)
EVENT_NAME_SLIDE = 'slide'
EVENT_NAME_SWITCH = 'switch'
EVENT_NAME_HIGHTLIGHT = 'highlight'

Y_SCALE = 1/8
X_SCALE = 1/2
PADDING = 20

class Scale(EventCallback, Component, CanvasWidget):

    __scale_components__ = [] #just names

    def all_components():
        return copy.deepcopy(Scale.__scale_components__)

    def __init__(self, canvas, name, width=1., height=1., size=11, position=None, highlight={}, key=None,
                    background_colour=COLOUR_LIGHT_BLUE, outline_thickness=OUTLINE_WIDTH, outline_colour=OUTLINE_COLOUR, 
                    slider_colour = COLOUR_BLUE, **kwargs):
        super(Scale, self).__init__(canvas, width=width, height=height, background_colour=background_colour, 
                                             outline_thickness=outline_thickness, outline_colour=outline_colour) 
        self.__state = 0 #the position (int) of the block slider
        EventCallback.register(self, name)
        Component.register(self, name)
        self.__size = size

        if position is None:
            position = size // 2
        else:
            position = min(max(position, 0), size-1)

        block =  BoxComponent(canvas, height=1/self.__size, outline_colour=outline_colour, 
                                outline_thickness=outline_thickness, colour=slider_colour)
        block.bind("<Button-1>")
        if key is not None:
            if not key.startswith("<"): #TODO check regex or something keys should be given in <SYMKEY> format (tkinter)
                key = "<{0}>".format(key)
            self.bind(key)

        block.__dict__['name'] = name #hacky...! TODO make less hacky, see Component.bind
        self.components['block'] = block

        for i in range(1, self.__size):
            line = LineComponent(self.canvas, 0, i * 1/self.__size, 1, i * 1/self.__size, colour=outline_colour, thickness=outline_thickness)
            self.components['line-' + str(i)] = line

        self.highlight = Highlight(canvas, self, **highlight)
        Scale.__scale_components__.append(self.name)

        self.slide(position)
    
    def slide(self, y):
        inc = self.content_height / self.__size
        self.__state += y
        self.__state = max(0, min(self.__size-1, self.__state))
        self.components['block'].y = self.y + inc * self.__state

    def sink(self, event):
        if event.data.label == EVENT_LABEL_CLICK:
            self.click_callback()
        elif event.data.label == EVENT_LABEL_KEY and event.data.action == 'press':
            self.click_callback()
        elif event.data.label == EVENT_NAME_SLIDE:
            self.slide(event.data.slide)

    def click_callback(self, *args):
        self.slide(self.__size // 2 - self.__state)


class WarningLight(EventCallback, Component, BoxComponent):

    __all_components__ = []
    
    def all_components():
        return WarningLight.__all_components__

    def __init__(self, canvas, name, width=1., height=1., state=0, prefered_state=0, key=None, 
                on_colour=COLOUR_GREEN, off_colour=COLOUR_RED, outline_thickness=OUTLINE_WIDTH,
                outline_colour=OUTLINE_COLOUR, highlight={}, grace=1):

        self.__state_colours = [off_colour, on_colour]
        self.__state = state
        self.__prefered_state = prefered_state #which state is good for the user
        colour = self.__state_colours[self.__state]
        super(WarningLight, self).__init__(canvas, width=width, height=height, colour=colour, outline_thickness=outline_thickness, outline_colour=OUTLINE_COLOUR)
        
        EventCallback.register(self, name)
        Component.register(self, name)

        self.bind("<Button-1>")
        if key is not None:
            if not key.startswith("<"): #TODO check regex or something keys should be given in <SYMKEY> format (tkinter)
                key = "<{0}>".format(key)
            self.bind(key)

        self.highlight = Highlight(canvas, self, **highlight)
        WarningLight.__all_components__.append(self.name)

        self.grace = grace # the light will wait atleast 1 second before switching off after the user interacts
        self.last_interacted = 0

    def update(self, state):
        self.__state = state
        self.colour = self.__state_colours[self.__state]
        #print("updated warning light:", self.name, self.__state, self.colour)

    def sink(self, event):
        #print(event)
        if event.data.label == EVENT_LABEL_CLICK or (event.data.label == EVENT_LABEL_KEY and event.data.action == 'press'):
            if self.__state != self.__prefered_state:
                self.update(self.__prefered_state)
                self.last_interacted = time.time()
        elif event.data.label == EVENT_NAME_SWITCH:
            if time.time() - self.grace > self.last_interacted: #only switch the light off if the user hasnt just turned it on!
                self.update(int(not bool(self.__prefered_state)))
            else:
                print("wait", self)

class SystemMonitorWidget(CanvasWidget):

    def __init__(self, canvas, config, width=480, height=640):
        super(SystemMonitorWidget, self).__init__(canvas, width=width, height=height, background_colour=BACKGROUND_COLOUR, padding=PADDING) 

        highlight = config['overlay']

        #warning lights
        scale_prop = 1/4

        #warning light widget
        self.warning_light_widget = CanvasWidget(canvas)
        self.components['warning_light_widget'] = self.warning_light_widget
        self.warning_lights = {}

        name = "{0}:{1}".format(WarningLight.__name__, str(0))
        options = dict(on_colour=COLOUR_GREEN, off_colour=BACKGROUND_COLOUR, prefered_state=1, key="<F5>")
        options.update(config.get(name, {}))
        self.warning_light_widget.components['warning_right'] = WarningLight(canvas, name=name, width=1/3, height=3/5, 
                                                                             highlight=highlight, **options)
        self.warning_lights[name] = self.warning_light_widget.components['warning_right']


        name = "{0}:{1}".format(WarningLight.__name__, str(1))
        options = dict(on_colour=COLOUR_RED,  off_colour=BACKGROUND_COLOUR, prefered_state=0, key="<F6>")
        options.update(config.get(name, {}))
        self.warning_light_widget.components['warning_left'] = WarningLight(canvas, name=name, width=1/3, height=3/5,
                                                                            highlight=highlight, **options)
        self.warning_lights[name] = self.warning_light_widget.components['warning_left']

        self.layout_manager.fill('warning_light_widget', 'X')
        self.layout_manager.split('warning_light_widget', 'Y', scale_prop)
        
        #place warning lights
        self.warning_light_widget.layout_manager.anchor('warning_left', 'EN')
        #self.warning_light_widget.layout_manager.fill('warning_left', 'Y')
        self.warning_light_widget.layout_manager.anchor('warning_right', 'WN')
        #self.warning_light_widget.layout_manager.fill('warning_right', 'Y')

        #scale widget
        scales = {k:v for k,v in config.items() if 'Scale' in k}

        self.scale_widget = CanvasWidget(canvas, padding=0, inner_sep=self.content_width/(len(scales)*2-1))
        self.components['scale_widget'] = self.scale_widget
        self.layout_manager.fill('scale_widget', 'X')
        self.layout_manager.split('scale_widget', 'Y', 1-scale_prop)

        
        self.scales = {}
        for i in range(len(scales)):
            name = "{0}:{1}".format(Scale.__name__, str(i))
            options = scales.get(name, {})

            scale = Scale(canvas, name=name, **options, highlight=highlight)
            self.scales[name] = scale

            self.scale_widget.components[str(i)] = scale

            self.scale_widget.layout_manager.fill(str(i), 'Y')
            self.scale_widget.layout_manager.split(str(i), 'X')
        
        #self.highlight = Highlight(canvas, self, **highlight) #TODO this blocks clicks, it can be fixed with some difficulty...
        
        #self.scale_widget.debug()
        #self.warning_light_widget.debug()

    @property
    def name(self):
        return self.__class__.__name__
