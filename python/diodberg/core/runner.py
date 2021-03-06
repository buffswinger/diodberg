import time
import threading


use_yappi = False
try:
    import yappi
except ImportError as err:
    sys.stderr.write("Error: failed to import module ({})".format(err))


class Runner(threading.Thread):
    """ A Runner is the primary execution thread for a Panel visualization. An
    abstract class, it takes a Panel of pixels and a Renderer and executes 
    a rendering action for that panel.
    """ 

    __slots__ = {'__lock', '__panel', '__name', 
                 '__renderer', '__sleepS', '__profile'}
    
    def __init__(self, panel, name, renderer, sleep, profile = False):
        super(Runner, self).__init__()
        self.daemon = True
        self.running = False
        self.__lock = threading.Lock()
        self.__panel = panel
        self.__name = name
        self.__renderer = renderer
        self.__sleepS = sleep
        self.__profile = profile
        if self.__profile and use_yappi:
            yappi.start()

    def __del__(self):
        if self.__profile and use_yappi:
            yappi.print_stats(sort_type = yappi.SORTTYPE_TSUB, 
                              limit = 15, 
                              thread_stats_on = False)

    def init(self):
        """ Initializes any environmental parameters based on the panel info.
        Defined by whatever subclasses Runner.
        """ 
        pass

    def fill(self):
        """ Iterate over the panel and change the pixel RGB values.
        Defined by whatever subclasses runner.
        """
        pass

    def run(self):
        self.running = True
        self.init()
        while self.running:
            self.__lock.acquire()
            self.fill()
            self.__renderer.render(self.__panel)
            self.__lock.release()
            time.sleep(self.__sleepS)
        
    def __get_panel(self): 
        return self.__panel
    def __set_panel(self, val): 
        self.__panel = val
    def __del_panel(self): 
        del self.__panel

    def __get_name(self): 
        return self.__name
    def __set_name(self, val): 
        self.__name = val
    def __del_name(self): 
        del self.__name

    def __get_renderer(self): 
        return self.__renderer
    def __set_renderer(self, val): 
        self.__renderer = val
    def __del_renderer(self): 
        del self.__renderer

    panel = property(__get_panel, __set_panel, __del_panel, "Panel.")
    name = property(__get_name, __set_name, __del_name, "Name of visualization.")
    renderer = property(__get_renderer, __set_renderer, __del_renderer, "Renderer.")

    def __repr__(self):
        return "Runner"


#TODO: Extend to multiple threads
class Controller(object):
    """ Controller initializes a set of Runner threads and shares execution between
    them. It this doesn't control switching between different runners, it's
    much useless.
    """
    def __init__(self, panel, renderer):
        self.__panel = panel
        self.__renderer = renderer
        self.__running = False

    def run(self, runner):
        # runner.panel = self.__panel
        # runner.renderer = self.__renderer
        try: 
            runner.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            runner.running = False
        finally:
            print "\nQuiting!"
            exit()
