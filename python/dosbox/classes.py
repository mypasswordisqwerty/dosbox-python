import dosbox


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls].__create__()
        return cls._instances[cls]


class UI:
    """ UI base class """

    def __init__(self):
        dosbox.Dosbox().ui = self

    def loop(self):
        """ input and process commands here """
        raise NotImplementedError()


class Disasm:
    """ Disassembler base class """

    def __init__(self):
        dosbox.Dosbox().dasm = self

    def disasm(self, loc, size, eip):
        """ disassemble """
        raise NotImplementedError()
