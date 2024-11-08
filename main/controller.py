import inputs

# Initiallize controller object
class Controller:
    def __init__(self):
        self.thiscode = None
        self.thisstate = None

    # What is being pressed?
    def readinputs(self):
        notsyncinp = False
        events = inputs.get_gamepad()
        for event in events:
            if str(event.ev_type) == "Absolute" or str(event.ev_type) == "Key":
                self.thiscode = event.code
                self.thisstate = event.state 
                notsyncinp = True

    # Return the presses
        return self.thiscode, self.thisstate, notsyncinp

        
