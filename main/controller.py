import inputs

# Initiallize controller object
class Controller:
    def __init__(self):
        self.inputkeys = {'ABS_X': 0,
                          'ABS_Y': 0,
                          'ABS_RX': 0,
                          'ABS_RY': 0,
                          'BTN_SELECT': 0}
        self.thiscode = None
        self.thisstate = None

    # What is being pressed?
    def readinputs(self):
        events = inputs.get_gamepad()
        for event in events:
            if str(event.ev_type) == "Absolute" or str(event.ev_type) == "Key":
                self.thiscode = event.code
                self.thisstate = event.state 

    # Return the presses
        return self.thiscode, self.thisstate

        
