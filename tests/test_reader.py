from hypothesis import given
from hypothesis.strategies import text

from actinide.reader import *
from actinide.ports import *
from actinide.types import *

from .forms import *

# Cases for the reader:

# * Given a form, can the reader recover it from its display?
@given(forms())
def test_reader(form):
    input = display(form, symbol_table)
    port = string_to_input_port(input)

    assert read(port, symbol_table) == form

# * Given a form and some trailing garbage, can the reader recover the form
#   without touching the garbage? This is only reliable with lists and conses.
@given(lists() | conses(), text())
def test_reader_with_trailing(form, text):
    input = display(form, symbol_table) + text
    port = string_to_input_port(input)

    assert read(port, symbol_table) == form
    assert read_port_fully(port) == text
