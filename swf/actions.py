
class Action(object):
    def __init__(self, code, length):
        self._code = code
        self._length = length
    
    @property
    def code(self):
        return self._code
    
    @property   
    def length(self):
        return self._length;
    
    @property
    def version(self):
        return 3
        
    def parse(self, data):
        # Do nothing. Many Actions don't have a payload. 
        # For the ones that have one we override this method.
        pass
    
    def tostring(self, indent=0):
        return "[Action] Code: 0x%x, Length: %d" % (self._code, self._length)

class ActionUnknown(Action):
    ''' Dummy class to read unknown actions '''
    def __init__(self, code, length):
        super(ActionUnknown, self).__init__(code, length)
    
    def parse(self, data):
        if self._length > 0:
            #print "skipping %d bytes..." % self._length
            data.skip_bytes(self._length)
    
    def tostring(self, indent=0):
        return "[ActionUnknown] Code: 0x%x, Length: %d" % (self._code, self._length)
        
class Action4(Action):
    ''' Base class for SWF 4 actions '''
    def __init__(self, code, length):
        super(Action4, self).__init__(code, length)
    
    @property
    def version(self):
        return 4

class Action5(Action):
    ''' Base class for SWF 5 actions '''
    def __init__(self, code, length):
        super(Action5, self).__init__(code, length)

    @property
    def version(self):
        return 5
        
class Action6(Action):
    ''' Base class for SWF 6 actions '''
    def __init__(self, code, length):
        super(Action6, self).__init__(code, length)

    @property
    def version(self):
        return 6
        
class Action7(Action):
    ''' Base class for SWF 7 actions '''
    def __init__(self, code, length):
        super(Action7, self).__init__(code, length)

    @property
    def version(self):
        return 7
                
# ========================================================= 
# SWF 3 actions
# =========================================================
class ActionGetURL(Action):
    CODE = 0x83
    def __init__(self, code, length):
        self.urlString = None
        self.targetString = None
        super(ActionGetURL, self).__init__(code, length)
        
    def parse(self, data):
        self.urlString = data.readString()
        self.targetString = data.readString()
        
class ActionGotoFrame(Action):
    CODE = 0x81
    def __init__(self, code, length):
        self.frame = 0
        super(ActionGotoFrame, self).__init__(code, length)

    def parse(self, data): 
        self.frame = data.readUI16()
        
class ActionGotoLabel(Action):
    CODE = 0x8c
    def __init__(self, code, length):
        self.label = None
        super(ActionGotoLabel, self).__init__(code, length)

    def parse(self, data): 
        self.label = data.readString()
        
class ActionNextFrame(Action):
    CODE = 0x04
    def __init__(self, code, length):
        super(ActionNextFrame, self).__init__(code, length)

class ActionPlay(Action):
    CODE = 0x06
    def __init__(self, code, length):
        super(ActionPlay, self).__init__(code, length)
    
    def tostring(self, indent=0):
        return "[ActionPlay] Code: 0x%x, Length: %d" % (self._code, self._length)
            
class ActionPreviousFrame(Action):
    CODE = 0x05
    def __init__(self, code, length):
        super(ActionPreviousFrame, self).__init__(code, length)
                
class ActionSetTarget(Action):
    CODE = 0x8b
    def __init__(self, code, length):
        self.targetName = None
        super(ActionSetTarget, self).__init__(code, length)

    def parse(self, data):
        self.targetName = data.readString()      
        
class ActionStop(Action):
    CODE = 0x07
    def __init__(self, code, length):
        super(ActionStop, self).__init__(code, length)
    
    def tostring(self, indent=0):
        return "[ActionStop] Code: 0x%x, Length: %d" % (self._code, self._length)
             
class ActionStopSounds(Action):
    CODE = 0x09
    def __init__(self, code, length):
        super(ActionStopSounds, self).__init__(code, length)   
        
class ActionToggleQuality(Action):
    CODE = 0x08
    def __init__(self, code, length):
        super(ActionToggleQuality, self).__init__(code, length)
        
class ActionWaitForFrame(Action):
    CODE = 0x8a
    def __init__(self, code, length):
        self.frame = 0
        self.skipCount = 0
        super(ActionWaitForFrame, self).__init__(code, length)

    def parse(self, data):
        self.frame = data.readUI16()
        self.skipCount = data.readUI8()
                              
# ========================================================= 
# SWF 4 actions
# =========================================================
class ActionAdd(Action4):
    CODE = 0x0a
    def __init__(self, code, length):
        super(ActionAdd, self).__init__(code, length)

class ActionAnd(Action4):
    CODE = 0x10
    def __init__(self, code, length):
        super(ActionAnd, self).__init__(code, length)
                       
# urgh! some 100 to go...


class SWFActionFactory(object):
    @classmethod
    def create(cls, code, length):
        if code == ActionPlay.CODE: return ActionPlay(code, length)
        if code == ActionStop.CODE: return ActionStop(code, length)
        else: return ActionUnknown(code, length)
        