import operator as op
import functools as f

from .types import *
from .builtin import make_registry

ACTINIDE_BINDINGS, ACTINIDE_VOIDS, ACTINIDE_FNS, ACTINIDE_BUILTINS, bind, void, fn, builtin = make_registry()

@fn
def __add__(*vals):
    return f.reduce(op.add, vals)

@fn
def __sub__(val, *vals):
    if vals:
        return f.reduce(op.sub, (val, *vals))
    return op.neg(val)

@fn
def __mul__(*vals):
    return f.reduce(op.mul, vals)

@fn
def __floordiv__(*vals):
    div = op.floordiv
    if any(decimal_p(val) for val in vals):
        div = op.truediv
    return f.reduce(div, vals)

@fn
def __eq__(a, b):
    return op.eq(a, b)

@fn
def __ne__(a, b):
    return op.ne(a, b)

@fn
def __lt__(a, b):
    return op.lt(a, b)

@fn
def __le__(a, b):
    return op.le(a, b)

@fn
def __gt__(a, b):
    return op.gt(a, b)

@fn
def __ge__(a, b):
    return op.ge(a, b)

@fn
def eq_p(a, b):
    return op.is_(a, b)

@fn
def equal_p(a, b):
    return op.eq(a, b)
