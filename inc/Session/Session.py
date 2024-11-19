
class Session:
    def __init__(self):
        self.command_registry = {
            "help": self.handle_help,
            "ls": self.handle_ls,
            "put": self.handle_put,
            "get": self.handle_get,
            "exit": self.handle_exit,
        }

    def handle_command(self, command_input):
        command, *args = command_input.split()
        handler = self.command_registry.get(command, self.handle_unknown)
        handler(args)

    def handle_help(self, args):
        pass

    def handle_ls(self, args):
        pass

    def handle_put(self, args):
        pass

    def handle_get(self, args):
        pass

    def handle_exit(self, args):
        pass

    def handle_unknown(self, args):
        pass

