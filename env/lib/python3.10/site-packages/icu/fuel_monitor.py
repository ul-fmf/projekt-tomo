import tkinter as tk
import random
import copy

from . import config as configuration

from .constants import BACKGROUND_COLOUR, COLOUR_GREEN, COLOUR_RED, COLOUR_LIGHT_BLUE, COLOUR_BLUE
from .constants import PUMP_HEIGHT, PUMP_WIDTH, OUTLINE_COLOUR, OUTLINE_WIDTH, PUMP_EVENT_RATE, PUMP_FLOW_RATE, PUMP_FAIL_SCHEDULE
from .constants import WARNING_OUTLINE_COLOUR, WARNING_OUTLINE_WIDTH, TANK_ACCEPT_POSITION, TANK_ACCEPT_PROPORTION


from .constants import BACKGROUND_COLOUR, OUTLINE_THICKESS, OUTLINE_COLOUR, FUEL_COLOUR
from .constants import TANK_BURN_RATE

from .constants import EVENT_LABEL_TRANSFER, EVENT_LABEL_FAIL, EVENT_LABEL_REPAIR, EVENT_LABEL_CLICK, EVENT_LABEL_MOVE, EVENT_LABEL_BURN


from . import event

from .event import Event, EventCallback

from .component import Component, CanvasWidget, SimpleComponent, BoxComponent, LineComponent, TextComponent, BaseComponent
from .highlight import Highlight


from pprint import pprint
from itertools import cycle

class FuelTank(EventCallback, Component, CanvasWidget):

    def __init__(self, canvas, x, y, width, height,  name, highlight, capacity=1000, fuel=100, 
                 background_colour=BACKGROUND_COLOUR, outline_thickness=OUTLINE_THICKESS, outline_colour=OUTLINE_COLOUR,
                 fuel_colour=FUEL_COLOUR, **kwargs):

        super(FuelTank, self).__init__(canvas, x=x, y=y, width=width, height=height, background_colour=background_colour)
 
        EventCallback.register(self, name)
        Component.register(self, name)

        self.capacity = capacity
        self.__fuel = fuel

        fh = (self.fuel / self.capacity) * height
       
        self.components['fuel'] = BoxComponent(canvas, x=x, y=y+height-fh, width=width, height=fh, colour=fuel_colour, outline_thickness=0)
        self.components['outline'] = BoxComponent(canvas, x=x, y=y, width=width, height=height, colour=None, outline_thickness=outline_thickness, outline_colour=outline_colour)

        self.highlight = Highlight(canvas, self, **highlight)
        self.components['text'] = TextComponent(canvas, x + width/2, y + height *11/10, self.fuel)

    
    @property
    def fuel(self):
        return self.__fuel

    @fuel.setter
    def fuel(self, value):
        self.__fuel = value
        self.components['text'].text = "{:.2f}".format(self.__fuel)

    def sink(self, event):
        raise NotImplemented("Tank events are handled by pumps?")

    def update(self, dfuel):
        self.fuel = min(max(self.fuel + dfuel, 0), self.capacity)
        
        fh = (self.fuel / self.capacity) * self.height
        self.components['fuel'].y = self.y + self.height - fh
        self.components['fuel'].height = fh

    def to_dict(self):
        dict(capacity=self.capacity, fuel=self.fuel, highlight=self.highlight.to_dict())

class FuelTankMain(FuelTank):

    def __init__(self, canvas, x, y, width, height, name, highlight, burn_rate=TANK_BURN_RATE, accept_position=TANK_ACCEPT_POSITION, 
                accept_proportion=TANK_ACCEPT_PROPORTION, background_colour=BACKGROUND_COLOUR, **kwargs):
        super(FuelTankMain, self).__init__(canvas, x, y, width, height, name, highlight, background_colour=background_colour, **kwargs)
        self.accept_position = accept_position
        self.accept_proportion = accept_proportion
        self.burn_rate = burn_rate #fuel per second
        self.event_rate = 10 #TODO config? 10 events per second

        py = height*(1-self.accept_position) - height*(self.accept_proportion/2)
        lx, ly, lw = x-0.1*width, y + py, width + width/5
        lh = height * self.accept_proportion
        
        #TODO accept box can go out of bounds of the tank...

        self.components['limit_box'] = BoxComponent(canvas, x=lx, y=ly, width=lw, height=lh, colour=COLOUR_LIGHT_BLUE, outline_thickness=0)
        self.components['limit_line'] = LineComponent(canvas, lx, ly + lh/2, lx + lw, ly + lh/2, colour=COLOUR_BLUE, thickness=3)
        self.components['back'] = BoxComponent(canvas, x=x, y=y, width=width, height=height, colour=background_colour, outline_thickness=0)
        self.components['fuel'].front()
        self.components['outline'].front()

        # in out of limits
        lim = self.limits
        self.__trigger_enter = self.fuel > lim[0] and self.fuel < lim[1]
        self.__trigger_leave = not self.__trigger_enter

        event.event_scheduler.schedule(self.__burn(), sleep=cycle([int(1000/self.event_rate)])) #start burning fuel

    def __burn(self):
        while True:
            dfuel = self.burn_rate / self.event_rate
            dfuel = min(dfuel, self.fuel)
            if self.fuel > 0:
                self.update(-dfuel)
                yield event.Event(self.name, 'Global', label=EVENT_LABEL_BURN, value=-dfuel)
            else:
                yield None

    @property
    def limits(self):
        cy, ch = self.capacity*self.accept_position, self.capacity*(self.accept_proportion/2)
        return cy - ch, cy + ch

    def update(self, dfuel):
        super(FuelTankMain, self).update(dfuel)
        lim = self.limits
        if self.fuel > lim[0] and self.fuel < lim[1]:
            #within the acceptable area
            if self.__trigger_enter:
                self.source('Global', label='fuel', acceptable=True)
                self.__trigger_enter = False
                self.__trigger_leave = True
                self.components['text'].text_colour = 'black'
        else:
            #print("out", lim, self.fuel)
            if self.__trigger_leave:
                self.source('Global', label='fuel', acceptable=False)
                self.__trigger_leave = False
                self.__trigger_enter = True
                self.components['text'].text_colour = 'red'

class FuelTankInfinite(FuelTank):

    def __init__(self, *args, **kwargs):
        super(FuelTankInfinite, self).__init__(*args, **kwargs)

    def update(self, dfuel):
        pass

class Pump(EventCallback, Component, CanvasWidget):

    __components__ = {} #just names

    def all_components():
        return {k:v for k,v in Pump.__components__.items()}

    ON_COLOUR = COLOUR_GREEN
    OFF_COLOUR = BACKGROUND_COLOUR
    FAIL_COLOUR = COLOUR_RED
    COLOURS = [ON_COLOUR, OFF_COLOUR, FAIL_COLOUR]

    def __init__(self, canvas, config, x, y, width, height, tank1, tank2, direction, options, highlight={}):
        #TODO refactor (options will be passed differently at some point)
        name = "{0}{1}".format(tank1.name.split(':')[1], tank2.name.split(':')[1])
        name = "{0}:{1}".format(Pump.__name__, name)
        self.__state = options[name]['state']
        super(Pump, self).__init__(canvas, x=x, y=y, width=width, height=height, background_colour=Pump.COLOURS[self.__state], outline_thickness=OUTLINE_WIDTH)

      
        
        default_config = configuration.default_pumps() #TODO remove
        config = config.get(name, default_config)

        self.flow_rate = options[name]['flow_rate']
        self.event_rate = options[name]['event_rate']

        EventCallback.register(self, name)
        Component.register(self, name)

        #parent.pumps[self.name] = self
        
        self.tank1 = tank1
        self.tank2 = tank2

        #p1, p2, p3 = direction(x, y, width, height)
        #self.components['arrow_line_1'] = LineComponent(canvas, *p1, *p2, thickness=2, colour=OUTLINE_COLOUR)
        #self.components['arrow_line_2'] = LineComponent(canvas, *p3, *p2, thickness=2, colour=OUTLINE_COLOUR)

        self.components['arrow'] = TextComponent(canvas, x + width/2, y + height/2, direction)
        self.bind("<Button-1>") #bind mouse events

        self.highlight = Highlight(canvas, self, **highlight)

        assert self.name not in Pump.__components__
        Pump.__components__[self.name] = self

    def right(x, y, width, height):
        n,d = 2,3
        return (x + width/d, y + height/d), (x + width*n/d, y + height/2), (x + width/d, y + height*n/d)

    def left(x, y, width, height):
        n,d = 2,3
        return (x + width*n/d, y + height/d), (x + width/d, y + height/2), (x + width*n/d, y + height*n/d)

    def up(x, y, width, height):
        n,d = 2,3
        return (x + width/d, y + height*n/d), (x + width/2, y + height/d), (x + width*n/d, y + height*n/d)
    
    def start(self):
        event.event_scheduler.schedule(self.__transfer(), sleep=cycle([int(1000/self.event_rate)]))

    def __transfer(self):
        while self.state == 0: #on
            yield self.transfer()

    def transfer(self):
        if self.tank1.fuel == 0 or self.tank2.fuel == self.tank2.capacity:
            return None #no event...

        flow = self.flow_rate / self.event_rate
        flow = min(flow, self.tank1.fuel) #if one tank is nearly empty, only transfer the fuel that is left
        flow = min(flow, self.tank2.capacity - self.tank2.fuel) #if the other tank is nearly full, only transfer fuel that fills it

        self.tank1.update(-flow)
        self.tank2.update(flow)
        return Event(self.name, 'Global', label=EVENT_LABEL_TRANSFER, value=flow) #notify global of the tank update

    def to_dict(self):
        return dict(state=self.state, highlight=self.highlight.to_dict())

    @property
    def name(self):
        return self._Component__name

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value
        self.background_colour = Pump.COLOURS[value]
        if value == 0:
            self.start()

    #def highlight(self, state): #TODO REMOVE
    #    self.highlight_state = state
    #    self.canvas.itemconfigure(self.highlight_rect, state=('hidden', 'normal')[state])

    def click_callback(self):
        if self.state != 2: #the pump has failed
            self.state = abs(self.__state - 1)

    def sink(self, event):
        if event.data.label == EVENT_LABEL_TRANSFER: #this may never happen... the event generator is now internal TODO refactor
            self.tank1.update(-event.data.value)
            self.tank2.update(event.data.value)
        elif event.data.label == EVENT_LABEL_FAIL:
            self.state = 2 # failed (unusable)
        elif event.data.label == EVENT_LABEL_REPAIR:
            self.state = 1 # not transfering (useable)
        elif event.data.label == EVENT_LABEL_CLICK:
            self.click_callback()


class Wing(CanvasWidget):
    
    def __init__(self, canvas, config, small_tank_name, med_tank_name, big_tank_name, highlight):
        super(Wing, self).__init__(canvas)

        width = height = 1 #everything will scale relative to the super widget

        #create full tanks
        fts = width / 4

        ftw_small = width / 6
        ftw_med = ftw_small * 1.4
        ftw_large = ftw_small * 2

        fth = height / 3
        margin = 0.08 #using padding here is a bit too tricky, maybe update TODO


        self.components['link'] = BoxComponent(canvas, x=fts, y=margin + fth/2 + fth/3, width=2 * fts, height=height-2*margin - fth - fth/3, outline_thickness=OUTLINE_WIDTH)

        self.components[small_tank_name] = FuelTank(canvas, fts - ftw_small/2, height - margin - fth, ftw_small, fth, small_tank_name, highlight, **config[small_tank_name])
        self.components[med_tank_name] = FuelTankInfinite(canvas, 3 * fts - ftw_med/2, height - margin - fth, ftw_med, fth, med_tank_name, highlight, **config[med_tank_name])
        
        btx, bty = 2 * fts - ftw_large/2, margin
        self.components[big_tank_name] = FuelTankMain(canvas, btx, bty, ftw_large, fth, big_tank_name, highlight, **config[big_tank_name])

        self.tanks = {small_tank_name:self.components[small_tank_name], med_tank_name:self.components[med_tank_name], big_tank_name:self.components[big_tank_name]}

        #create pumps
        cx = (fts + ftw_small/2)
        ex = (3 * fts - ftw_med/2)
        ecx = (cx + ex) / 2
        ecy = height - margin - fth / 2

        pw = 1.5 * width / 16
        ph = 1.5 * height / 20

        #TODO refactor config argument (just pass what is needed)
        self.components['pump21'] = Pump(canvas, config, ecx - pw/2, ecy - ph/2, pw, ph, self.components[med_tank_name], self.components[small_tank_name], "<", config, highlight=highlight)
        self.components['pump13'] = Pump(canvas, config, fts - pw/2, height/2 - ph/2, pw, ph, self.components[small_tank_name], self.components[big_tank_name], "^", config, highlight=highlight)
        self.components['pump23'] = Pump(canvas, config, 3 * fts - pw/2, height /2 - ph/2, pw, ph, self.components[med_tank_name], self.components[big_tank_name], "^", config, highlight=highlight)
       
        self.pumps = {p.name:p for k,p in self.components.items() if 'pump' in k}

        #self.components['link'].back()
   
class FuelWidget(CanvasWidget):

    def __init__(self, canvas, config, width, height):
        super(FuelWidget, self).__init__(canvas, width=width, height=height, background_colour=BACKGROUND_COLOUR)

        self.tanks = {}
        self.pumps = {}

        highlight = config['overlay'] #highlight options
        
        name = FuelTank.__name__ + ":{0}"

        self.wing_left  = Wing(canvas, config, name.format("C"), name.format("E"), name.format("A"), highlight)
        self.wing_right = Wing(canvas, config, name.format("D"), name.format("F"), name.format("B"), highlight)
        
        self.tanks.update(self.wing_left.tanks)
        self.tanks.update(self.wing_right.tanks)
        self.pumps.update(self.wing_left.pumps)
        self.pumps.update(self.wing_right.pumps)

        self.components['wl'] = self.wing_left
        self.components['wr'] = self.wing_right

        self.layout_manager.fill('wl', 'Y')
        self.layout_manager.fill('wr', 'Y')
        self.layout_manager.split('wl', 'X', .5)
        self.layout_manager.split('wr', 'X', .5)
        
        tank_a_name = name.format('A')
        tank_b_name = name.format('B')

        (ax, ay) = self.tanks[tank_a_name].position
        (aw, ah) = self.tanks[tank_a_name].size
        ax = ax + aw / 2
        ay = ay + ah / 2

        (bx, by) = self.tanks[tank_b_name].position
        (bw, bh) = self.tanks[tank_b_name].size

        bx = bx + bw / 2
        by = by + bh / 2

        self.components['AB'] = SimpleComponent(canvas, canvas.create_line(ax+aw/2,ay-ah/6,bx-bw/2,by-bh/6, width=OUTLINE_WIDTH))
        self.components['BA'] =  SimpleComponent(canvas, canvas.create_line(ax+aw/2,ay+ah/6,bx-bw/2,by+bh/6, width=OUTLINE_WIDTH))

        w, h = self.wing_left.components['pump21'].size


        #TODO refactor config (pass only what is needed)
        self.components['pumpAB'] = Pump(canvas, config, (ax+bx)/2 - w/2, ay-ah/6 - h/2, w, h, self.tanks[tank_a_name], self.tanks[tank_b_name], ">", config, highlight=highlight)
        self.components['pumpBA'] = Pump(canvas, config, (ax+bx)/2 - w/2, ay+ah/6 - h/2, w, h, self.tanks[tank_b_name], self.tanks[tank_a_name], "<", config, highlight=highlight)

        self.pumps[self.components['pumpAB'].name] = self.components['pumpAB']
        self.pumps[self.components['pumpBA'].name] = self.components['pumpBA']

        print(Pump.all_components().keys())

    def highlight(self, child=None):
        if child is None:
            print("highlight self")
        elif child in self.pumps:
            print("highlight pump")
            pump = self.pumps[child]

        elif child in self.tanks:
            print("highlight tank")
        else:
            raise ValueError("Invalid child widget: {0}".format(child))