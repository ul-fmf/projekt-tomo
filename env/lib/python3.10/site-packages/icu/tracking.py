import tkinter as tk
import random

from .constants import TRACKING_LINE_COLOUR, TRACKING_TARGET_SPEED, BACKGROUND_COLOUR
from .constants import WARNING_OUTLINE_COLOUR, WARNING_OUTLINE_WIDTH
from .constants import EVENT_LABEL_MOVE, EVENT_LABEL_KEY


from .event import Event, EventCallback
from .component import Component

from .component import Component, CanvasWidget, SimpleComponent, BoxComponent, LineComponent, BaseComponent
from .highlight import Highlight
    
class Target(CanvasWidget):

    def __init__(self, canvas, radius, inner_radius, line_thickness=5):
        if line_thickness > 5:
            raise ValueError("line_thickness above 5 may lead to visual artefacts... fix incoming")
        circle = SimpleComponent(canvas, canvas.create_oval(0,0,radius*2,radius*2, outline=TRACKING_LINE_COLOUR, width=line_thickness))
        dot = SimpleComponent(canvas, canvas.create_oval(radius-inner_radius*2, radius-inner_radius*2, radius+inner_radius*2, radius+inner_radius*2, fill=TRACKING_LINE_COLOUR, width=0))
        super(Target, self).__init__(canvas, components={'circle':circle, 'dot':dot})

class Tracking(EventCallback, Component, CanvasWidget):

    __instance__ = None

    def all_components():
        return [Tracking.__instance__.name]

    def __init__(self, canvas, config, size, **kwargs):
        super(Tracking, self).__init__(canvas, width=size, height=size, background_colour=BACKGROUND_COLOUR, **kwargs)

        name = "{0}:{1}".format(Target.__name__, str(0))
        EventCallback.register(self, name)
        Component.register(self, name)
    
        #draw the tracking pattern
        line_size = size/16
        line_thickness = 3
        edge = line_thickness // 2 + 1

        ts = size/12

        def add(**kwargs): #add components
            for k,v in kwargs.items():
                self.components[k] = v

        target = Target(canvas, ts, ts/10)
        target.position = (size/2 - ts, size/2 - ts)

        self.key_events = {'Left':(-1,0), 'Right':(1,0), 'Up':(0,-1), 'Down':(0,1)}

        edge = 0 #TODO remove edge...

        add(target=target)
        #four corners
        #NW
        add(NW1=LineComponent(canvas, 0, edge, line_size, edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(NW2=LineComponent(canvas, edge, 0, edge, line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        #SW
        add(SW1=LineComponent(canvas, 0, size-edge, line_size, size-edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(SW2=LineComponent(canvas, edge, size, edge, size-line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        #SE
        add(SE1=LineComponent(canvas, size, size-edge, size-line_size, size-edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(SE2=LineComponent(canvas, size-edge, size, size-edge, size-line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        #NE
        add(NE1=LineComponent(canvas, size, edge, size-line_size, edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))   
        add(NE2=LineComponent(canvas, size-edge, 0, size-edge, line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        #main middle lines
        add(M1=LineComponent(canvas, size/2, 0, size/2, size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M2=LineComponent(canvas, 0, size/2, size, size/2, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        #middle lines
        add(M3=LineComponent(canvas, size/2 - line_size, edge, size/2 + line_size, edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M4=LineComponent(canvas, size/2 - line_size, size-edge, size/2 + line_size, size-edge, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        add(M5=LineComponent(canvas, edge, size/2-line_size, edge, size/2+line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M6=LineComponent(canvas, size-edge, size/2-line_size, size-edge, size/2+line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        #middle lines.... middle ;)
        add(M7=LineComponent(canvas, size/2 - line_size/2, edge + size/8, size/2 + line_size/2, edge + size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M8=LineComponent(canvas, size/2 - line_size, edge + 2*size/8, size/2 + line_size, edge + 2*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        add(M9=LineComponent(canvas, size/2 - line_size, -edge + 6*size/8, size/2 + line_size, -edge + 6*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M10=LineComponent(canvas, size/2 - line_size/2, -edge + 7*size/8, size/2 + line_size/2, -edge + 7*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        add(M11=LineComponent(canvas, edge + size/8, size/2 + line_size/2, edge + size/8, size/2 - line_size/2, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M12=LineComponent(canvas, edge + 2*size/8, size/2 + line_size, edge + 2*size/8, size/2 - line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        
        add(M13=LineComponent(canvas, -edge + 6*size/8, size/2 + line_size, -edge + 6*size/8, size/2 - line_size, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))
        add(M14=LineComponent(canvas, -edge + 7*size/8, size/2 + line_size/2, -edge + 7*size/8, size/2 - line_size/2, colour=TRACKING_LINE_COLOUR, thickness=line_thickness))

        #middle rectangle
        #add(B=BoxComponent(canvas, edge + 3*size/8, edge + 3*size/8, -edge + 2*size/8, -edge + 2*size/8, outline_colour=TRACKING_LINE_COLOUR, outline_thickness=line_thickness, dash=(4,2)))
        dash = (4,8)
        add(B1=LineComponent(canvas, edge + 3*size/8, edge + 3*size/8, edge + 5*size/8, edge + 3*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness, dash=dash))
        add(B2=LineComponent(canvas, edge + 3*size/8, edge + 5*size/8, edge + 5*size/8, edge + 5*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness, dash=dash))
        add(B3=LineComponent(canvas, edge + 3*size/8, edge + 3*size/8, edge + 3*size/8, edge + 5*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness, dash=dash))
        add(B4=LineComponent(canvas, edge + 5*size/8, edge + 3*size/8, edge + 5*size/8, edge + 5*size/8, colour=TRACKING_LINE_COLOUR, thickness=line_thickness, dash=dash))

        #self.c.size = (size-200, size-50) #test resize
        highlight = config['overlay']
        self.highlight = Highlight(canvas, self, **highlight)
        
        assert Tracking.__instance__ is None #there can only be one tracking widget
        Tracking.__instance__ = self
        
        if config[name].get('invert', True):
            self.invert = (-1,-1)
        else:
            self.invert = (1,1)
        self.step = config[name].get('step', 1)

        self.bind("<Left>")
        self.bind("<Right>")
        self.bind("<Up>")
        self.bind("<Down>")


    def sink(self, event):
        #print(event)
        x, y = self.components['target'].position
        w, h = self.components['target'].size
        rx, ry = self.position
        rw, rh = self.components['background'].size #TODO fix the aspect ratio code - e.g. use content_size?

        sx, sy = rw / 200, rh / 200 #the default speed (relative to he size of the widget)

        if event.data.label == EVENT_LABEL_KEY:
            dx, dy = 0, 0
            key = event.data.key
            #for key in event.data.key:
            dx += self.key_events[key][0]
            dy += self.key_events[key][1]
            dx, dy = sx * dx * self.invert[0], sy * dy * self.invert[1]

        else:
            #TODO speed here?
            dx = event.data.dx * self.invert[0]
            dy = event.data.dy * self.invert[1]

        
        nx, ny = x + dx, y + dy
        #clip bounds
        nx = max(rx, min(rx + rw - w, nx))
        ny = max(ry, min(ry + rh - h, ny))

        self.components['target'].position = (nx, ny)

        cx, cy = nx - rx - rw/2 + w/2, ny - ry - rh/2 + h/2 #centered (relative) position of the target
        self.source('Global', label=EVENT_LABEL_MOVE, dx=dx, dy=dy, x=cx, y=cy)


    # keep aspect ratio TODO move all this to a layout manager or special widget
    def resize(self, dw, dh):
        aspect = min(self.size)
        pw, ph = aspect - dw, aspect - dh
        sw, sh = aspect / pw, aspect / ph
        #print(self, "scale:", sw, sh, "from:", pw,ph, "to:", self.width, self.height)
        for c in self.components.values(): #scale each widget
            c.size = (c.width * sw, c.height * sh)
           
            c.x = self.x + (c.x - self.x) * sw
            c.y = self.y + (c.y - self.y) * sh

    @BaseComponent.size.setter
    def size(self, value):
        d = min(value) - min(self.size)
        self._BaseComponent__width, self._BaseComponent__height = value
        
        self.resize(d, d)
        for observer in self.observers['size']:
            observer((d, d))

    @BaseComponent.width.setter
    def width(self, value):
        d = min(value, self._BaseComponent__height) - min(self.size)
        self._BaseComponent__width = value
        if d != 0:
            self.resize(d, d)
            for observer in self.observers['size']:
                observer((d, d))
    
    @BaseComponent.height.setter
    def height(self, value):
        d = min(self._BaseComponent__width, value) - min(self.size)
        self._BaseComponent__height =  value
        if d != 0:
            self.resize(d, d)
            for observer in self.observers['size']:
                observer((d, d))

        

       



