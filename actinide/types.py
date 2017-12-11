# ## Actinide Types

import builtins as b
from collections import namedtuple
from decimal import Decimal, InvalidOperation

# Circular import. Hard to avoid: Procedure calls `eval`, `eval` calls
# `lambda_`, `lambda_` eventually calls `Procedure`. We indirect the call
# through the module object to avoid problems with import order.
from . import evaluator as e

from .environment import *
from .builtin import Registry

An = Registry()

# ### Nil
#
# Nil is a type with a single value, usually taken to denote no value.

nil = An.bind('nil', None)

@An.fn
def nil_p(value):
    return value is None

def display_nil(value):
    return '()'

# ### Booleans
#
# The true and false values.

true = An.bind('#t', True)
false = An.bind('#f', False)

@An.fn
def boolean_p(value):
    return value is true or value is false

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

@An.fn
def integer(value):
    return int(value)

@An.fn
def integer_p(value):
    return isinstance(value, int)

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

@An.fn
def decimal(value):
    return Decimal(value)

@An.fn
def decimal_p(value):
    return isinstance(value, Decimal)

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

@An.fn
def string(value):
    return str(value)

@An.fn
def string_p(value):
    return not symbol_p(value) and isinstance(value, str)

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
        return self.value
    def __repr__(self):
        return f'Symbol({repr(self.value)})'

# bind manually, fix the symbol table
def symbol(string, symbol_table):
    return symbol_table[string]

@An.fn
def symbol_p(value):
    return isinstance(value, Symbol)

def read_symbol(value, symbol_table):
    return symbol(value, symbol_table)

def display_symbol(value):
    return str(value)

# ### Conses
#
# Pairs.

Cons = namedtuple('Cons', 'head tail')

@An.fn
def cons(head, tail):
    return Cons(head, tail)

@An.fn
def cons_p(value):
    return isinstance(value, Cons)

@An.fn
def head(cons):
    return cons.head

@An.fn
def tail(cons):
    return cons.tail

@An.builtin
def uncons(cons):
    return head(cons), tail(cons)

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

@An.fn
def list(*elems):
    if elems:
        head, *tail = elems
        return cons(head, list(*tail))
    else:
        return nil

@An.fn
def list_p(value):
    return nil_p(value) or cons_p(value) and list_p(tail(value))

@An.fn
def append(list, *lists):
    if not lists:
        return list
    if nil_p(list):
        return append(*lists)
    value, next = head(list), tail(list)
    return cons(value, append(next, *lists))

@An.fn
def length(list):
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

# ### Vectors

@An.fn
def vector(*elems):
    return b.list(elems)

@An.fn
def vector_p(value):
    return isinstance(value, b.list)

@An.fn
def vector_to_list(value):
    return list(*value)

@An.fn
def list_to_vector(value):
    return flatten(list)

@An.fn
def vector_length(value):
    return b.len(value)

@An.fn
def vector_get(value, index):
    return value[index]

@An.fn
def vector_set(value, index, elem):
    value[index] = elem
    return value

@An.fn
def vector_add(value, *elems):
    value.extend(elems)
    return value

def display_vector(value, symbols):
    return f"<vector: [{' '.join(display(elem, symbols) for elem in value)}]>"

# ### Procedures

class ProcedureError(Exception):
    pass

class Procedure(object):
    def __init__(self, body, formals, environment, macros, symbols):
        self.environment = environment
        self.macros = macros
        self.symbols = symbols
        self.body = body
        self.continuation = self.compile()
        self.formals, self.tail_formal = self.parse_formals(formals)

    def compile(self, continuation=None):
        return e.eval(self.body, self.symbols, continuation)

    def invocation_environment(self, *args):
        if b.len(args) < b.len(self.formals) or \
            b.len(args) > b.len(self.formals) and not self.tail_formal:
            args_syntax = append(list(*self.formals), self.tail_formal)
            call_syntax = list(*args)
            raise ProcedureError(f'Procedure with arguments {display(args_syntax, self.symbols)} called with arguments {display(call_syntax, self.symbols)}')

        named_args = b.list(zip(self.formals, args))
        tail_arg = []
        if self.tail_formal:
            tail_list = list(*args[b.len(self.formals):])
            tail_binding = (self.tail_formal, tail_list)
            tail_arg.append(tail_binding)

        return Environment(named_args + tail_arg, self.environment)

    def __call__(self, *args):
        call_env = self.invocation_environment(*args)
        call_macros = Environment(parent=self.macros)
        return e.run(self.continuation, call_env, call_macros, ())

    @classmethod
    def parse_formals(cls, formals):
        names = []
        while not nil_p(formals) and cons_p(formals):
            formal, formals = uncons(formals)
            names.append(formal)
        return names, formals

@An.fn
def procedure_p(value):
    return callable(value)

def display_procedure(proc, symbols):
    if isinstance(proc, Procedure):
        formals = display(append(list(*proc.formals), proc.tail_formal), symbols)
        body = display(proc.body, symbols)
        return f'<procedure: (lambda {formals} {body})>'
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
    if vector_p(value):
        return display_vector(value, symbols)
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
