# Core functions
from .builtin import make_registry

ACTINIDE_BINDINGS, ACTINIDE_VOIDS, ACTINIDE_FNS, ACTINIDE_BUILTINS, bind, void, fn, builtin = make_registry()

@fn
def begin(*args):
    if args:
        return args[-1]
    return None

@builtin
def values(*args):
    return args
