import inputs

# Initiallize controller object
class Controller:
    def __init__(self):
        self.inputkeys = dict.fromkeys(['ABS_X','ABS_Y','ABS_RX','ABS_RY','BTN_SELECT'])

    # What is being pressed?
    def readinputs(self):
        events = inputs.get_gamepad()
        for event in events:
            if str(event.ev_type) == "Absolute" or str(event.ev_type) == "Key":
                if str(event.code) in self.inputkeys:
                    self.inputkeys[str(event.code)] = event.state
                else:
                   print(f"No inputkey found for event {event.code}")

    # Return the presses
        return self.inputkeys

        
