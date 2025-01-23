class Player:
    '''
    Just a class stores global variables cross jobs
    '''
    def __init__(self, **kwargs):
        self.inventory = {}
        self.shop_inventory = {}
        self.load_data(kwargs)

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, key):
        return self.__dict__.get(key, None)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def load_data(self, data):
        for key, value in data.items():
            self.__dict__[key] = value

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return f"<Player: {self.__dict__}>"

    def __repr__(self):
        return self.__str__()

data = Player()
