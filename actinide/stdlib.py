import operator as op
import functools as f

from .types import *
from .builtin import Registry

An = Registry()

@An.fn
def __add__(*vals):
    return f.reduce(op.add, vals)

@An.fn
def __sub__(val, *vals):
    if vals:
        return f.reduce(op.sub, (val, *vals))
    return op.neg(val)

@An.fn
def __mul__(*vals):
    return f.reduce(op.mul, vals)

@An.fn
def __floordiv__(*vals):
    div = op.floordiv
    if any(decimal_p(val) for val in vals):
        div = op.truediv
    return f.reduce(div, vals)

@An.fn
def __eq__(a, b):
    return op.eq(a, b)

@An.fn
def __ne__(a, b):
    return op.ne(a, b)

@An.fn
def __lt__(a, b):
    return op.lt(a, b)

@An.fn
def __le__(a, b):
    return op.le(a, b)

@An.fn
def __gt__(a, b):
    return op.gt(a, b)

@An.fn
def __ge__(a, b):
    return op.ge(a, b)

@An.fn
def eq_p(a, b):
    return op.is_(a, b)

@An.fn
def equal_p(a, b):
    return op.eq(a, b)

@An.fn
def and_(a, b):
    return op.and_(a, b)

@An.fn
def or_(a, b):
    return op.or_(a, b)

@An.fn
def not_(a):
    return not a

def let(symbols, bindings, *body):
    if nil_p(bindings):
        return list(*body)

    binding, bindings = uncons(bindings)
    name, value = flatten(binding)

    return list(
        append(
            list(symbols['lambda'], list(name)),
            let(symbols, bindings, *body),
        ),
        value
    )

@An.fn
def concat(*strings):
    return ''.join(strings)
