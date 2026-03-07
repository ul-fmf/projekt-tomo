"""
    An overlay may be displayed at a given positon on the GUI, make use of the Overlay class to do this.

    @Author: Benedict Wilkins
    @Date: 2020-04-02 21:57:11
"""

from .event import Event, EventCallback
from .component import Component, PolyComponent, BaseComponent


class Overlay(EventCallback, Component, PolyComponent):
    """
        A GUI widget that is placed above other widgets. Accepts 'move' and 'place' events to move the widget.
    """

    def __init__(self, canvas, component):
        super(Overlay, self).__init__(canvas, component)
        name = "{0}:{1}".format(Overlay.__name__, str(0))

        EventCallback.register(self, name)
        Component.register(self, name) 

    def sink(self, event):
        #print(event)
        if event.data.label == 'place':
            self.x = event.data.x 
            self.y = event.data.y 
        elif event.data.label == 'move':
            self.x += event.data.dx
            self.y += event.data.dy
        elif event.data.label == 'rotate':
            self.rotate(event.data.angle)
        elif event.data.label == 'saccade':
            self.x = event.data.x - self.width/2
            self.y = event.data.y - self.height/2
            self.hide()
        elif event.data.label == 'gaze':
            self.x = event.data.x - self.width/2
            self.y = event.data.y - self.height/2
            self.show()





