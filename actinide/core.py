# Core functions
from .builtin import Registry
An = Registry()

@An.builtin
def values(*args):
    return args
