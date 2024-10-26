class Singleton:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            return cls.instance
        else:
            return cls.instance

    @classmethod
    def get_instance(cls):
        if cls.instance:
            return cls.instance
        else:
            raise ValueError("Tried to fetch non-instantiated Singleton type", {"type": cls.__name__})
