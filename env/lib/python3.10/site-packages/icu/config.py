import json
import os
import re
import random
import copy

from types import SimpleNamespace
from collections import defaultdict

from itertools import cycle, islice


class ConfigurationError(Exception):
    pass

# size 800,800
# banner 25

# scales 240, 350

# fuel padding 250 


# =================================== # =================================== # =================================== # 
# =================================== # ======== ALL CONFIG OPTIONS ======= # =================================== # 
# =================================== # =================================== # =================================== #

def tasks():
    return SimpleNamespace(**{k:k for k in ['system', 'fuel', 'track']})

def default_config_screen():
    return dict(#screen_width=None,  #handled by post processing
                #screen_height=None, #handled by post processing
                screen_size=(800,700),
                #screen_x = None, #handled by post processing
                #screen_y = None, #handled by post processing
                screen_position=(0,0),
                screen_min_size=(100,100),
                screen_max_size=(2000,2000),
                screen_full=False,
                screen_resizable=True,
                screen_aspect=None,
                background_colour='grey')

def default_task_options():
    return   {"system" : True, "track" : True,"fuel" : True}

def default_event_schedule():
    return {"Scale:0" :         default_scale_schedule(),
            "Scale:1" :         default_scale_schedule(),
            "Scale:2" :         default_scale_schedule(),
            "Scale:3" :         default_scale_schedule(),
            "WarningLight:0" :  default_warning_light_schedule(),
            "WarningLight:1" :  default_warning_light_schedule(),
            "Target:0" :        default_target_schedule()}

def default_event_generator():
    return {"ScaleComponent" : "ScaleEventGenerator"}

def default_scale_schedule():
    return uniform(1000,10000) 

def default_warning_light_schedule():
    return uniform(1000,10000) 

def default_pump_schedule():
    return uniform(0,20000)

def default_target_schedule():
    return cycle([300])

# TODO config should contain everything --- create a default for all widgets!
def default_scales():
    return {"Scale:0" : default_scale("<F1>"),
            "Scale:1" : default_scale("<F2>"),
            "Scale:2" : default_scale("<F3>"),
            "Scale:3" : default_scale("<F4>")}

def default_scale(key):
    return {'size':11, 'position':5, 'key':key}

def default_warning_lights():
    return {'WarningLight:0' : {'state':1, 'key':"<F5>", 'grace':2}, 'WarningLight:1' : {'state':0, 'key':"<F6>", 'grace':2}}

def  default_tanks():
    return {
        "FuelTank:A" : {"capacity":2000, "fuel":1000, "burn_rate":6, "accept_position":0.5, "accept_proportion":0.3},
        "FuelTank:B" : {"capacity":2000, "fuel":1000, "burn_rate":6, "accept_position":0.5, "accept_proportion":0.3},
        "FuelTank:C" : {"capacity":1000, "fuel":100},
        "FuelTank:D" : {"capacity":1000, "fuel":100},
        "FuelTank:E" : {"capacity":1000, "fuel":1000},
        "FuelTank:F" : {"capacity":1000, "fuel":1000}}

def default_pumps():
    default_pump = { "flow_rate": 100, "event_rate": 10, "state": 1}

    return {"Pump:AB" : copy.deepcopy(default_pump),
            "Pump:BA" : copy.deepcopy(default_pump), 
            "Pump:FD" : copy.deepcopy(default_pump),
            "Pump:EA" : copy.deepcopy(default_pump),
            "Pump:CA" : copy.deepcopy(default_pump),
            "Pump:EC" : copy.deepcopy(default_pump),
            "Pump:DB" : copy.deepcopy(default_pump),
            "Pump:FB" : copy.deepcopy(default_pump)}
    

def default_tracking():
    return {} #TODO

def default_input():
    return {"mouse" : True,
            "keyboard" : True,
            "joystick" : False,
            "eyetracker" : {
                "stub" : True,
                "enabled" : True,
                "sample_rate" : 100,
                "calibrate" : False
            }}


def default_overlay():
    return dict(enable=True, transparent=True, outline=True, arrow=True)

def default_config():
    return dict(**default_config_screen(), task=default_task_options(), schedule=default_event_schedule(), overlay=default_overlay(), input=default_input(),
                **default_scales(), **default_warning_lights(), **default_tanks(), **default_pumps(), **default_tracking())

ScreenOptions = SimpleNamespace(**{k:k for k in default_config_screen().keys()})
# TODO other options

# =================================== # =================================== # =================================== # 

# =================================== # =================================== # =================================== # 
# =================================== # ========= DISTRIBUTIONS =========== # =================================== # 
# =================================== # =================================== # =================================== #

class Distribution: #must be an iterable...
    
    def __iter__(self):
        return self

    def __next__(self):
        return self.sample()

class uniform(Distribution):

    def __init__(self, a, b):
        try:
            #assert a >= 0 and b >= 0
            a = float(a)
            b = float(b)
            self.a = min(a,b)
            self.b = max(a,b)
        except:
            raise ConfigurationError("Invalid arguments for uniform distribution: {0}, {1}, must be numbers > 0".format(a,b))

    def sample(self):
        return random.uniform(self.a, self.b)

class normal(Distribution):

    def __init__(self, mu, sigma, decay=1.):
        try:
            self.mu = float(mu)
            self.sigma = float(sigma)
            self.decay = float(decay) #multiplicative decay?
        except:
            raise ConfigurationError("Invalid arguments for uniform distribution: {0}, {1}, must be numbers".format(mu, sigma))

    def sample(self):
        self.mu = self.mu * self.decay
        return max(0, random.gauss(self.mu, self.sigma)) #not thread safe?

distributions = lambda: {k.__name__:k for k in Distribution.__subclasses__()}

# =================================== # =================================== # =================================== # 

def is_type(*types): #validate type(s) 
    def _is_type(**kwargs): #expects a singleton dictionary
        assert len(kwargs) == 1
        k = next(iter(kwargs.keys()))
        v = kwargs[k]
        #print(k,v,types)
        if not isinstance(v, tuple(types)):
            raise ConfigurationError("Invalid value '{0}' for '{1}', must be one of type: {2}.".format(v, k, tuple([t.__name__ for t in types])))
        return v
    return _is_type

def is_coord():
    def _is_coord(**kwargs):
        k = next(iter(kwargs.keys()))
        v = kwargs[k]
        if isinstance(v, list) and len(v) == 2 and isinstance(v[0], (int, float)) and isinstance(v[1], (int,float)):
            return tuple(v)
        else:
            raise ConfigurationError("Invalid value '{0}' for '{1}', must be a list of length 2 and contain only numbers.".format(v, k))
    return _is_coord

def condition(cond):
    def _condition(**kwargs):
        assert len(kwargs) == 1
        k = next(iter(kwargs.keys()))
        v = kwargs[k]
        if not cond(v):
            raise ConfigurationError("Invalid value '{0}' for '{1}'.".format(v, k))
        return v
    return _condition
        
def get_option(k, group, _options=None):
    if _options is None:
        _options = options

    k = k.split(":")[0]
    if k in _options:
        option = _options[k]
        assert isinstance(option, Option)
        if option.group == group:
            return option

    raise ConfigurationError("Invalid config option: \"{0}\" for config group: \"{1}\"".format(k, group))

def validate_options(group, _options=None):
    return (lambda **kwargs : {k:get_option(k, group, _options=_options)(**{k:v}) for k,v in next(iter(kwargs.values())).items()})

class Option:
    
    def __init__(self, group, fun):
        self.group =  group
        self.__fun = fun

    def __call__(self, **kwargs):
        return self.__fun(**kwargs)

# CONFIG OPTIONS ARE ALL DEFINED IN THE DICTIONARY BELOW - EACH SHOULD BE VALIDATED



target_options = dict(
    step               = Option('target', is_type(int, float)),
    invert             = Option('target', is_type(bool))
)

warninglight_options = dict(
    grace               = Option('warning_light', is_type(int, float)),
    key                 = Option('warning_light', is_type(str)),
    state               = Option('warning_light', is_type(int)),
    on_colour           = Option('warning_light', is_type(str)),
    off_colour          = Option('warning_light', is_type(str)),
    outline_colour      = Option('warning_light', is_type(str)),
    outline_thickness   = Option('warning_light', is_type(int))
)

scale_options = dict(
    key                 = Option('warning_light', is_type(str)),
    size                = Option('scale', is_type(int)),
    position            = Option('scale', is_type(int)),
    background_colour   = Option('scale', is_type(str)),
    outline_colour      = Option('scale', is_type(str)),
    outline_thickness   = Option('scale', is_type(int)),
    slider_colour       = Option('scale', is_type(str))
)

pump_options = dict(
    flow_rate           = Option('pump', is_type(int)),
    event_rate          = Option('pump', is_type(int)),
    #cosmetic
    scale               = Option('pump', is_type(float))
)

tank_options = dict(
    burn_rate           = Option('tank', is_type(int, float)),
    accept_position     = Option('tank', is_type(int, float)),
    accept_proportion   = Option('tank', is_type(int, float)),
    capacity            = Option('tank', is_type(int, float)),
    fuel                = Option('tank', is_type(int, float)),
    # cosmetic
    fuel_colour         = Option('tank', is_type(str)),
    background_colour   = Option('tank', is_type(str)),
    outline_colour      = Option('tank', is_type(str)),
    outline_thickness   = Option('tank', is_type(int)),
)

eyetracker_options = dict(
    enabled             = Option('eyetracker', is_type(bool)),
    stub                = Option('eyetracker', is_type(bool)),
    calibrate           = Option('eyetracker', is_type(bool)),
    sample_rate         = Option('eyetracker', is_type(int)),
)

options = dict(

            main            = Option('-', validate_options('main')),

            #TODO validate these arguments?
            Pump            = Option('main', validate_options('pump', _options=pump_options)),
            Target          = Option('main', validate_options('target', _options=target_options)),
            WarningLight    = Option('main', validate_options('warning_light', _options=warninglight_options)),
            Scale           = Option('main', validate_options('scale', _options=scale_options)),
            FuelTank        = Option('main', validate_options('tank', _options=tank_options)),

            screen_width    = Option('main', is_type(int, float)),
            screen_height   = Option('main', is_type(int, float)),
            screen_size     = Option('main', is_coord()),
            screen_x        = Option('main', is_type(int, float)),
            screen_y        = Option('main', is_type(int, float)),
            screen_position        = Option('main', is_coord()),

            screen_full            = Option('main', is_type(bool)),
            screen_resizable       = Option('main', is_type(bool)),
            screen_aspect          = Option('main', is_coord()),
            screen_min_size        = Option('main', is_coord()),
            screen_max_size        = Option('main', is_coord()),
            background_colour       = Option('main', is_type(str)),
            
            schedule        = Option('main', lambda **kwargs: {k:Validator.is_schedule(**{k:v}) for k,v in next(iter(kwargs.values())).items()}),
            
            task            = Option('main', validate_options('task')),
            system          = Option('task', is_type(bool)),
            track           = Option('task', is_type(bool)),
            fuel            = Option('task', is_type(bool)),

            input           = Option('main',  validate_options('input')),
            mouse           = Option('input', is_type(bool)),
            keyboard        = Option('input', is_type(bool)),
            joystick        = Option('input', is_type(bool)),

            eyetracker      = Option('input', validate_options('eyetracker', _options=eyetracker_options)),

            generators      = Option('main', lambda **kwargs: None), #TODO

            overlay             = Option('main',    validate_options('overlay')),
            enable              = Option('overlay', is_type(bool)),
            arrow               = Option('overlay', is_type(bool)),
            transparent         = Option('overlay', is_type(bool)),
            outline             = Option('overlay', is_type(bool)),
            highlight_thickness = Option('overlay', is_type(int)),
            highlight_colour    = Option('overlay', is_type(str)),

    )


import collections.abc

def update(d, u): #recursive dictionary update
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

class Validator:

    def validate_iter(k, v):
        for i in v:
            if not isinstance(i, (int, float)):
                raise ConfigurationError("Invalid value '{0}' for '{1}' in repeating schedule {2}, must be a number.".format(i, k, v))
        return v

    def validate_list(k, v):
        if len(v) > 0 and isinstance(v[0], list):
            if len(v) > 1:
                raise ConfigurationError("Invalid value '{0}' for '{1}', a repeating schedule is specified through the use of double square brackets: [[...]].".format(k, v))
            v = Validator.validate_iter(k, v[0])
            return cycle(v)
        else:
            v = Validator.validate_iter(k, v)
            return iter(v)

    def validate_str(k, v):
        pattern = '\w+\(((\w|\d)+,)*((\w|\d)+)?\)'
        r = re.match(pattern, re.sub(r"\s+", "", v))
        if r is not None:
            name, args = v.split('(')
            dists = distributions()
            if name in dists:
                args = args[:-1].split(",")
                try:
                    return dists[name](*args)
                except Exception as e:
                    raise ConfigurationError("Invalid value '{0}' for '{1}', failed to build distribution, perhaps the arguments were invalid.".format(v,k)) from e
            else:
                raise ConfigurationError("Invalid value '{0}' for '{1}', distribution not found, valid distributions include: {2}".format(v,k,tuple(distributions().keys())))


    def is_schedule(**kwargs): #validate schedule (number, list, tuple, str)
        k = next(iter(kwargs.keys()))
        v = kwargs[k]
        if isinstance(v, (int, float)): #schedule a single event
            return v
        elif isinstance(v, list):
            return Validator.validate_list(k, v)
        elif isinstance(v, str): #build schedule object
            return Validator.validate_str(k, v)
        raise ConfigurationError("Invalid value '{0}' for '{1}', must be a number, tuple, list or distribution.".format(v,k))


    def __call__(self, **kwargs):
        config =  validate_options('main')(**{'main':kwargs}) #{k:get_option(k, 'main')(**{k:v}) for k,v in kwargs.items()}

        # ====== POST PROCESSING ====== # 
        #TOOD move this somewhere more suitable
        result = default_config()
        result = update(result, config)
        #from pprint import pprint
        #pprint(result)

        result['screen_size'] = (result.get('screen_width', result['screen_size'][0]), result.get('screen_height', result['screen_size'][1]))
        result['screen_position'] = (result.get('screen_x', result['screen_position'][0]), result.get('screen_y', result['screen_position'][1]))
        result['screen_width'], result['screen_height'] = result['screen_size']
        result['screen_x'], result['screen_y'] = result['screen_position']
        return result

validate = Validator()

def save(path, **kwargs):
    """ Save config to a file.

    Args:
        path (str): path to config file (config file is always called 'config.json')
    """
    if not path.endswith('config.json'):
        path = os.path.join(path, 'config.json')
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find config file at location: {0}".format(path))
    with open(path, 'w') as f:
        # maybe validate here?
        json.dump(kwargs, f, indent=4, sort_keys=True)
    
def load(path):
    """ Load a config file.

    Args:
        path (str): path to config file

    Returns:
        dict: a dictionary containing loaded config
    """
    path = os.path.abspath(path)
    if not path.endswith('config.json'):
        path = os.path.join(path, 'config.json')
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find config file at location: {0}".format(path))
    print("USING CONFIG FILE: {0}".format(path))
    with open(path, 'r') as f: 
        data = json.load(f)
        result = validate(**data)
        return result

def reset(path):
    """ Reset config file to default values.

    Args:
        path (str): path to config file
    """
    if not path.endswith('config.json'):
        path = os.path.join(path, 'config.json')
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find config file at location: {0}".format(path))
    with open(path, 'w') as f:
        json.dump(kwargs, f, indent=4, sort_keys=True)

if __name__ == "__main__":

    def run():
        path = 'icu/'
        save(path, **default_config())
        config = load(path)

        for k,v in config.items():
            print(k, v, type(v))
    run()

    #regex tests...
    from pprint import pprint
    for i in default_config_screen():
        print(i, ":")
    print()
    for i in default_event_schedule():
        print(i, ":")
    
    """
    def match(v):
        pattern = '\w+\(((\w|\d),)*((\w|\d)+)?\)'
        r = re.match(pattern, v)
        return r

    print(match('uniform(0,1000)'))
    print(match('uniform(10)'))
    print(match('uniform()'))
    """