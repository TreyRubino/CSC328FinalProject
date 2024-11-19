from inc.Controller import ServerController

# maybe this can be the 'View'
try:
    server_controller = ServerController()
    server_controller.start()
except Exception as e:
    print(f"An error has occurred: {e}")
    server_controller.stop()