# ## Actinide Types

from collections import namedtuple
from decimal import Decimal, InvalidOperation

# Circular import. Hard to avoid: Procedure calls `eval`, `eval` calls
# `lambda_`, `lambda_` eventually calls `Procedure`. We indirect the call
# through the module object to avoid problems with import order.
from . import evaluator as e

from .environment import *
from .builtin import make_registry

ACTINIDE_BINDINGS, ACTINIDE_VOIDS, ACTINIDE_FNS, ACTINIDE_BUILTINS, bind, void, fn, builtin = make_registry()

# ### Nil
#
# Nil is a type with a single value, usually taken to denote no value.

nil = bind('nil', None)

@fn
def nil_p(value):
    return value is None

@fn
def read_nil(value):
    return nil

def display_nil(value):
    return '()'

# ### Booleans
#
# The true and false values.

true = bind('#t', True)
false = bind('#f', False)

@fn
def boolean_p(value):
    return value is true or value is false

@fn
def read_boolean(value):
    if value == '#t':
        return true
    if value == '#f':
        return false
    return None

def display_boolean(value):
    return '#t' if value else '#f'


# ### Integers
#
# These are fixed-precision numbers with no decimal part, obeying common notions
# of machine integer arithmetic. They support large values.

integer = bind('integer', int)

@fn
def integer_p(value):
    return isinstance(value, integer)

@fn
def read_integer(value):
    try:
        return integer(value)
    except ValueError:
        return nil

def display_integer(value):
    return str(value)

# ### Decimals
#
# These are variable-precision numbers, which may have a decimal part.

decimal = bind('decimal', Decimal)

@fn
def decimal_p(value):
    return isinstance(value, decimal)

@fn
def read_decimal(value):
    try:
        return decimal(value)
    except InvalidOperation:
        return nil

def display_decimal(value):
    return str(value)

# ### Strings
#
# Sequences of characters.

string = bind('string', str)

@fn
def string_p(value):
    return not symbol_p(value) and isinstance(value, string)

@fn
def read_string(value):
    value = value[1:-1]
    value = value.replace('\\"', '"')
    value = value.replace('\\\\', '\\')
    return value

def display_string(value):
    value = value.replace('\\', '\\\\')
    value = value.replace('"', '\\"')
    return f'"{value}"'

# ### Symbols
#
# Short, interned strings used as identifiers. Interning is handled by a
# SymbolTable.

class Symbol(object):
    def __init__(self, value):
        self.value = value
    def __hash__(self):
        return hash(self.value)
    def __str__(self):
        return f"{self.value}"
    def __repr__(self):
        return f'Symbol({repr(self.value)})'

# bind manually, fix the symbol table
def symbol(string, symbol_table):
    return symbol_table[string]

@fn
def symbol_p(value):
    return isinstance(value, Symbol)

@fn
def read_symbol(value, symbol_table):
    return symbol(value, symbol_table)

def display_symbol(value):
    return str(value)

# ### Conses
#
# Pairs.

Cons = namedtuple('Cons', 'head tail')

@fn
def cons(head, tail):
    return Cons(head, tail)

@fn
def cons_p(value):
    return isinstance(value, Cons)

@fn
def head(cons):
    return cons.head

@fn
def tail(cons):
    return cons.tail

def display_cons(value, symbols):
    parts = []
    while cons_p(value):
        parts.append(display(head(value), symbols))
        value = tail(value)
    if not nil_p(value):
        parts.append('.')
        parts.append(display(value, symbols))
    return '(' + ' '.join(parts) + ')'

# ### Lists

@fn
def list(*elems):
    if elems:
        head, *tail = elems
        return cons(head, list(*tail))
    else:
        return nil

@fn
def list_p(value):
    return nil_p(value) or cons_p(value) and list_p(tail(value))

@fn
def append(list, *lists):
    if not lists:
        return list
    if nil_p(list):
        return append(*lists)
    value, next = head(list), tail(list)
    return cons(value, append(next, *lists))

@fn
def len(list):
    l = 0
    while not nil_p(list):
        l += 1
        list = tail(list)
    return l

def flatten(list):
    r = []
    while not nil_p(list):
        r.append(head(list))
        list = tail(list)
    return r

# ### Procedures

class Procedure(object):
    def __init__(self, body, formals, environment, macros, symbols):
        self.body = body
        self.continuation = e.eval(body, symbols, None)
        self.formals = formals
        self.environment = environment
        self.macros = macros

    def __call__(self, *args):
        call_env = self.invocation_environment(*args)
        call_macros = Environment(parent=self.macros)
        return e.run(self.continuation, call_env, call_macros, ())

    def invocation_environment(self, *args):
        return Environment(zip(self.formals, args), self.environment)

@fn
def procedure_p(value):
    return callable(value)

def display_procedure(proc, symbols):
    if isinstance(proc, Procedure):
        formals = ' '.join(display(formal, symbols) for formal in proc.formals)
        body = display(proc.body, symbols)
        return f'<procedure: (lambda ({formals}) {body})>'
    return f'<builtin: {proc.__name__}>'

# ### General-purpose functions

# Bind manually, fixing the symbol table at the bind site
def display(value, symbols):
    if quote_p(value, symbols):
        return display_quote(value, symbols)
    if cons_p(value):
        return display_cons(value, symbols)
    if symbol_p(value):
        return display_symbol(value)
    if string_p(value):
        return display_string(value)
    if nil_p(value):
        return display_nil(value)
    if boolean_p(value):
        return display_boolean(value)
    if integer_p(value):
        return display_integer(value)
    if decimal_p(value):
        return display_decimal(value)
    if procedure_p(value):
        return display_procedure(value, symbols)
    # Give up and use repr to avoid printing `None`.
    return repr(value)

def quote_p(value, symbols):
    return cons_p(value) and head(value) in [
        symbols[q]
        for q in ['quote', 'quasiquote', 'unquote', 'unquote-splicing']
    ]

def display_quote(value, symbols):
    quote, form = flatten(value)
    if quote == symbols['quote']:
        return "'" + display(form, symbols)
    if quote == symbols['quasiquote']:
        return "`" + display(form, symbols)
    if quote == symbols['unquote']:
        return "," + display(form, symbols)
    if quote == symbols['unquote-splicing']:
        return ",@" + display(form, symbols)
    # emergency fallback
    return display_cons(value, symbols)
