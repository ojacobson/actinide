from hypothesis.strategies import integers, decimals as hypo_decimals, booleans, characters, text, tuples, lists as hypo_lists, just, one_of
from hypothesis.strategies import deferred, recursive

from actinide import tokenizer as t
from actinide.symbol_table import *
from actinide.types import *

# Generators for forms. Where these generators create a symbol, they will use
# the global symbol table defined in this module. Do not do this in your own
# code! A global symbol table is a memory leak, and only the fact that tests
# exit before they can do any substantial damage prevents this from being a
# bigger problem.
#
# Each generator produces the parsed version of a form.

symbol_table = SymbolTable()

# Generates nil.
def nils():
    return just(None)

# Generates integers.
def ints():
    return integers()

# Generates language decimals.
def decimals():
    return hypo_decimals(allow_nan=False, allow_infinity=False)

# Generates booleans.
def bools():
    return booleans()

# Generates strings.
def strings():
    return text()

# Generates any character legal in a symbol, which cannot be part of some other
# kind of atom.
def symbol_characters():
    return characters(blacklist_characters='01234567890#' + t.whitespace + t.parens + t.quotes + t.string_delim + t.comment_delim)

# Generates symbols guaranteed not to conflict with other kinds of literal. This
# is a subset of the legal symbols.
def symbols():
    return text(symbol_characters(), min_size=1)\
        .map(lambda item: symbol_table[item])

def quoted_forms():
    return tuples(
        one_of(
            symbol_table[q]
            for q in ['quote', 'quasiquote', 'unquote', 'unquote-splicing']
        ),
        deferred(lambda: forms),
    ).map(lambda elems: list(*elems))

# Generates atoms.
def atoms():
    return one_of(
        nils(),
        ints(),
        decimals(),
        bools(),
        strings(),
        symbols(),
    )

# Generates arbitrary conses, with varying depth. This may happen to generate
# lists by accident.
def conses():
    return recursive(
        tuples(atoms(), atoms()).map(lambda elems: cons(*elems)),
        lambda children: tuples(children | atoms(), children | atoms()).map(lambda elems: cons(*elems)),
    )

# Generates lists, with varying depth.
def lists():
    return recursive(
        hypo_lists(atoms()).map(lambda elems: list(*elems)),
        lambda children: hypo_lists(children | atoms()).map(lambda elems: list(*elems)),
    )

# Generates random forms.
def forms():
    return one_of(nils(), ints(), bools(), strings(), symbols(), conses(), lists())
