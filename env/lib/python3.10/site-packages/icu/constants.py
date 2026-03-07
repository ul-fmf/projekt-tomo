
def rgb(*colour):
    """Creates a hex string from rgb args
    Args:
        colour (*int): rgb values
    Returns:
        str: rgb hex string
    """
    return "#%02x%02x%02x" % colour 

# EVENT

EVENT_LABEL_CLICK = 'click'
EVENT_LABEL_SLIDE = 'slide'
EVENT_LABEL_SWITCH = 'switch'
EVENT_LABEL_HIGHTLIGHT = 'highlight'
EVENT_LABEL_MOVE = 'move'
EVENT_LABEL_REPAIR = 'repair'
EVENT_LABEL_FAIL = 'fail'
EVENT_LABEL_TRANSFER = 'transfer'
EVENT_LABEL_BURN = 'burn'
EVENT_LABEL_KEY = 'key'

# GENERAL

JOYSTICK = False #are we using a joystick?
EYETRACKING = True #are we using eyetracking?

COLOUR_GREEN = '#90c73e'
COLOUR_RED = '#f2644d'


BACKGROUND_COLOUR = 'lightgray'
OUTLINE_WIDTH = 2 #TODO remove
OUTLINE_COLOUR = 'black'

OUTLINE_THICKESS = 2
OUTLINE_COLOUR = "BLACK"



WARNING_OUTLINE_COLOUR = 'red'
WARNING_OUTLINE_WIDTH = 7

COLOUR_BLUE = '#255f9e' #'#4882b2'
COLOUR_LIGHT_BLUE = '#92c6d9'



MAIN_BANNER_COLOUR = '#0000fe'
MAIN_BANNER_HEIGHT = 16

#SYSTEM MONITOR
SYSTEM_MONITOR_WIDTH = 400
SYSTEM_MONITOR_HEIGHT = 400


#WARNING_LIGHT_MIN_WIDTH = 90
#WARNING_LIGHT_MIN_HEIGHT = 60



SYSTEM_MONITOR_SCALE_POSITIONS = [0,1,2,3,4] #this can be random...

#---------- TRACKING MONITOR ----------
TRACKING_LINE_COLOUR = '#268fea'

#No. pixels to move when a target move event is triggered
TRACKING_TARGET_SPEED = 2


#---------- FUEL MONITOR ----------

FUEL_COLOUR = COLOUR_GREEN

FUEL_MONITOR_WIDTH = 800
FUEL_MONITOR_HEIGHT = 400



PUMP_HEIGHT = 20
PUMP_WIDTH = 40

# size of he acceptable region

TANK_ACCEPT_PROPORTION = 0.2 # what is the acceptable region for fuel in tank?
TANK_ACCEPT_POSITION = 0.5 

TANK_BURN_RATE = 5 # burn 5 fuel per second in main tanks (A, B)
EVENT_RATE = 10 #10 events per second by default


#N fuel-transfer events per second
PUMP_EVENT_RATE = 10 

#fuel-transfer per second
PUMP_FLOW_RATE = {
    'AB': 100,
    'BA': 100,
    'CA': 20,
    'DB': 20,
    'EA': 30,
    'EC': 30,
    'FB': 30,
    'FD': 30
}

def RANDOM_SLEEP_SCHEDULE(min=0, max=30000):
    import random
    while True:
        yield random.randint(min, max)

#PUMP_FAIL_SCHEDULE = 3000 #fail every 3 seconds
#PUMP_FAIL_SCHEDULE = [10000,5000,7000,1000] #fail after N seconds and repeat
PUMP_FAIL_SCHEDULE = RANDOM_SLEEP_SCHEDULE()

