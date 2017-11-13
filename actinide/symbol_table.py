from .types import Symbol

class SymbolTable(dict):
    def __missing__(self, key):
        self[key] = result = Symbol(key)
        return result

