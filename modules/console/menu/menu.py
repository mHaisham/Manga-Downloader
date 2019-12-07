from whaaaaat import prompt


class Menu:
    def __init__(self, message, options, action=True, key=lambda val: val):
        """

        :param options: key-action pairs
        :param action:
        :param loop:
        """
        self.message = message
        self.action = action

        if type(options) == list:
            print(options)
            self._options = {key(item): '' for item in options}
            self.action = False
        else:
            self._options = options

    @property
    def options(self):
        return self._options

    def loop(self, condition=True):
        while condition:
            self.prompt()

    def prompt(self):

        key = prompt(dict(
            type='list',
            name='menu',
            message=self.message,
            choices=list(self.options.keys())
        ))['menu']

        if self.action:
            self.options[key]()
        else:
            return key
