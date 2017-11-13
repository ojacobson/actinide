from hypothesis import given
from hypothesis.strategies import integers, text

from actinide.ports import *

@given(text(), integers(min_value=1, max_value=2**32 - 1))
def test_read(input, n):
    port = string_to_input_port(input)
    output = read_port(port, n)

    assert input.startswith(output)
    assert (len(output) == 0 and len(input) == 0) != (0 < len(output) <= n)
    assert output + read_port_fully(port) == input

@given(text(), integers(min_value=1, max_value=2**32 - 1))
def test_peek(input, n):
    port = string_to_input_port(input)
    output = peek_port(port, n)

    assert input.startswith(output)
    assert (len(output) == 0 and len(input) == 0) != (0 < len(output) <= n)
    assert read_port_fully(port) == input

@given(text(), integers(min_value=1, max_value=2**32 - 1))
def test_read_fully(input, n):
    port = string_to_input_port(input)
    output = read_port_fully(port)

    assert output == input
