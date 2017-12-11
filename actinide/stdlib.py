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
def and_(*vals):
    return all(vals)

@An.fn
def or_(*vals):
    return any(vals)

@An.fn
def not_(a):
    return not a

def let(symbols, bindings, *body):
    def beginify(*forms):
        if len(forms) == 1:
            form, = forms
            return form
        return list(symbols['begin'], *forms)

    if nil_p(bindings):
        return beginify(*body)

    binding, bindings = uncons(bindings)
    name, value = flatten(binding)

    return list(
        append(
            list(symbols['lambda'], list(name)),
            list(let(symbols, bindings, *body)),
        ),
        value
    )

@An.fn
def concat(*strings):
    return ''.join(strings)

def single_valued(fn):
    def wrapper(*args, **kwargs):
        result, = fn(*args, **kwargs)
        return result
    return wrapper

@An.fn
def filter(pred, vals):
    return list(*b.filter(single_valued(pred), flatten(vals)))

@An.fn
def map(fn, vals):
    return list(*b.map(single_valued(fn), flatten(vals)))

@An.fn
def reduce(fn, vals):
    return f.reduce(single_valued(fn), flatten(vals))
