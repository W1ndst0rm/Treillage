class Identifier(dict):
    def __init__(self, native: int, partner: str = ""):
        dict.__init__(self, native=native, partner=partner)
