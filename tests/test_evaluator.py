from hypothesis import given, event

from actinide.evaluator import *
from actinide.environment import *
from actinide.types import *

from .programs import *

# Cases for the evaluator:

# * Given a program, does it produce the expected evaluation?
@given(programs())
def test_evaluator(program_result):
    program, result, bindings = program_result
    environment = Environment()
    macros = Environment()
    assert run(eval(program, symbol_table, None), environment, macros) == result
    for symbol, value in bindings:
        assert environment[symbol] == value
