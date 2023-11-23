
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonBase(metaclass=SingletonMeta):
    def __init__(self, name=None):
        self.name = name

    @classmethod
    def delete_instance(cls):
        if cls in cls._instances:
            del cls._instances[cls]

    @classmethod
    def get_instance(cls):
        if cls not in cls._instances:
            instance = cls()
            cls._instances[cls] = instance
        return cls._instances[cls]