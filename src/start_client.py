from inc.Controller import ClientController

try:
    client_controller = ClientController()
    client_controller.start()
except Exception as e:
    print(f"An error has occurred: {e}")
    client_controller.stop()
