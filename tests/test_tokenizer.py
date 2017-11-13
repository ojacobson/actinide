from hypothesis import given

from actinide.tokenizer import *
from actinide.ports import *

from .tokens import spaced_token_sequences, tokens, nontokens

# Cases for the tokenizer:

# * any single token: reads back that token.
@given(tokens())
def test_tokenizer_single_token(input):
    port = string_to_input_port(input)

    assert read_token(port) == input

# * any input guaranteed not to contain a token: reads back None, consuming the
#   whole input in the process.
@given(nontokens())
def test_tokenizer_no_token(input):
    port = string_to_input_port(input)

    assert read_token(port) == None

# * any sequence of separator-token pairs: if the pairs are coalesced into a
#   single giant input, does the tokenizer recover the tokens?
@given(spaced_token_sequences())
def test_tokenizer_spaced_sequence(spaced_tokens):
    input = ''.join(''.join(pair) for pair in spaced_tokens)
    tokens = [token for (_, token) in spaced_tokens]

    port = string_to_input_port(input)
    def iterate_read_token(port):
        token = read_token(port)
        while token is not None:
            yield token
            token = read_token(port)

    assert list(iterate_read_token(port)) == tokens

