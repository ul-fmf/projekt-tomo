
from .event import EventCallback
from .component import BaseComponent, BoxComponent

def all_highlights():
    return Highlight.__all_highlights__

class Highlight(EventCallback):

    __all_highlights__ = {}

    def __init__(self, canvas, component, state=False, highlight_thickness=4, highlight_colour='red', outline=True, transparent=False, **kwargs):
        assert isinstance(component, BaseComponent)
        super(Highlight, self).__init__()
        if kwargs.get('enable', True): #otherwise this is a stub
            name = "{0}:{1}".format(Highlight.__name__, component.name)
            EventCallback.register(self, name)

            self.__canvas = canvas 
            self.__component = component
            self.__highlight_thickness = highlight_thickness

            self.component.observe('size', self.resize)
            self.component.observe('position', self.move)

            background_colour = (highlight_colour, None)[int(transparent)]
            outline = (0, highlight_thickness)[int(outline)]

            self.__box = BoxComponent(self.canvas, x=component.x, y=component.y, width=component.width, height=component.height,
                                        colour=background_colour, outline_thickness=highlight_thickness, outline_colour=highlight_colour, stipple="gray25")

            #self.__box.front()
            if not state:
                self.off()

            Highlight.__all_highlights__[self.name] = self

    def sink(self, event):
        if "value" in event.data.__dict__: #if no value is given, flip the highlight on/off
            (self.off, self.on)[int(event.data.value)]() #love it
        else:
            self.flip()
        #print("SINK: ", event)
        self.source('Global', label='highlight', value=self.is_on) # emit a global event (for external systems)
    
    def to_dict(self):
        return dict(state=self.is_on(), highlight_thickness=self.highlight_thickness, highlight_colour=self.highlight_colour)

    def flip(self):
        if self.is_on:
            self.off()
        else:
            self.on()

    def on(self):
        self.__box.show()
       
    def off(self):
        self.__box.hide()

    @property
    def is_on(self):
        return not self.__box.is_hidden()
    
    @property
    def is_off(self):
        return self.__box.is_hidden()

    @property
    def highlight_thickness(self):
        return self.__box.outline_thickness
    
    @highlight_thickness.setter
    def highlight_thickness(self, value):
        self.__box.highlight_thickness = value

    @property
    def highlight_colour(self):
        return self.__box.outline_colour

    @highlight_colour.setter
    def highlight_colour(self, value):
         self.__box.outline_colour = value
        
    @property
    def component(self):
        return self.__component

    @property
    def canvas(self):
        return self.__canvas

    def move(self, _):
        self.__box.front() #TODO this is a work around until the layout manager supports layering
        self.__box.position = self.component.position

    def resize(self, dsize):
        dx, dy = dsize
        sx, sy = self.__box.size
        self.__box.size = (sx + dx, sy + dy)

    def __call__(self):
        self.state = not self.state
