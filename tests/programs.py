from hypothesis.strategies import integers, decimals, booleans, text, tuples
from hypothesis.strategies import one_of, composite, deferred

from actinide.types import *
from actinide.environment import *
from actinide.symbol_table import *

symbol_table = SymbolTable()

def literals():
    return one_of(
        booleans(),
        integers(),
        decimals(allow_nan=False, allow_infinity=False),
        text(),
    ).map(lambda value: (value, (value,), []))

def symbols():
    return text().map(lambda symb: symbol_table[symb])

def values():
    return literals()

@composite
def ifs(draw, conds, trues, falses):
    cond, (cond_result,), cond_bindings = draw(conds)
    true, true_result, true_bindings = draw(trues)
    false, false_result, false_bindings = draw(falses)

    expr = list(symbol_table['if'], cond, true, false)
    result = true_result if cond_result else false_result
    bindings = cond_bindings + (true_bindings if cond_result else false_bindings)

    return expr, result, bindings

def if_exprs():
    return ifs(exprs(), exprs(), exprs())

def if_progs():
    return ifs(exprs(), programs(), programs())

@composite
def defines(draw):
    symbol = draw(symbols())
    value, (value_result,), value_bindings = draw(values())
    return (
        list(symbol_table['define'], symbol, value),
        (),
        value_bindings + [(symbol, value_result)],
    )

def exprs():
    return deferred(lambda: one_of(literals(), if_exprs()))

def programs():
    return deferred(lambda: one_of(literals(), defines(), if_progs()))

