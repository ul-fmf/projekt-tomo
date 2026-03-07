import tkinter as tk

from . import panel
from .constants import MAIN_BANNER_COLOUR, MAIN_BANNER_HEIGHT

from .component import BaseComponent, CanvasWidget, SimpleLayoutManager, EmptyComponent

from .event import EventCallback

from .overlay import Overlay

OUTER_PADDING = 0 ##??? maybe...
MOUSE_BIND = "<Button-1>"

class MainPanel(tk.Canvas, EventCallback):

    def __init__(self, parent, width, height, background_colour='blue'):
        super(MainPanel, self).__init__(parent, width=width, height=height, bg=background_colour)
        
        EventCallback.register(self, "Canvas")
        
        #create banners
        layout_manager = SimpleLayoutManager(inner_sep=0)
        layout_manager = None
        self.__main = CanvasWidget(self, x=OUTER_PADDING, y=OUTER_PADDING, width=width-OUTER_PADDING*2, height=width-OUTER_PADDING*2, layout_manager=layout_manager)

        
        self.top_frame = CanvasWidget(self)
        self.bottom_frame = CanvasWidget(self)
        self.padding_frame = EmptyComponent()

        self.banner1 = EmptyComponent()
        self.banner2 = EmptyComponent()


        self.__main.components['top'] = self.top_frame
        self.__main.components['bottom'] = self.bottom_frame
        self.__main.components['banner1'] = self.banner1
        self.__main.components['banner2'] = self.banner2    
    

        self.__main.layout_manager.split('banner1','Y', prop=25/700)
        self.__main.layout_manager.split('top', 'Y', prop=350/700)
        self.__main.layout_manager.split('banner2', 'Y', prop=25/700)
        self.__main.layout_manager.split('bottom', 'Y', prop=300/700)

        self.__main.layout_manager.fill('top', 'X')
        self.__main.layout_manager.fill('bottom', 'X')

        self.__overlay = None

        # mouse clicks should be registered to the canvas

        self.bind(MOUSE_BIND, self.on_click)

    def sink(self, event):
        pass #events should never be sent here?

    def on_click(self, event):
        overlapping = self.find_overlapping(event.x, event.y, event.x, event.y)
        bound = BaseComponent.bound(MOUSE_BIND)
        for overlap in overlapping:
            if overlap in bound:
                #print("BOUND: ", bound[overlap])
                clickable = bound[overlap]
                self.source(clickable.name, label="click", x=event.x, y=event.y)

    @property
    def size(self):
        return self.__main.size

    @property
    def position(self):
        return self.__main.position

    def resize(self, event):
        #print(event.width, event.height)
        if self.winfo_width() != event.width or self.winfo_height() != event.height:
            self.config(width=event.width, height=event.height)
            self.__main.size = (event.width-OUTER_PADDING*2, event.height-OUTER_PADDING*2)
            self.pack()

    def overlay(self, component):
        self.__overlay = Overlay(self, component)
        self.__overlay.front()
        self.__main.components['overlay'] = self.__overlay

    @property
    def top(self):
        return self.top_frame

    @property
    def bottom(self):
        return self.bottom_frame