import inputs

def main():
	while True:
		events = inputs.get_gamepad()
		for event in events:
			if str(event.ev_type) == "Absolute" or str(event.ev_type) == "Key":
				print("event code " + str(event.code))
				print("event state " + str(event.state))
				print("----")
if __name__ == "__main__":
	main()


