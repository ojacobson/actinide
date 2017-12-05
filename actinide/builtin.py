# ## Tools for binding Python functions into a lisp environment.

from functools import wraps

dunder_names = {
    '__add__': '+',
    '__sub__': '-',
    '__mul__': '*',
    '__floordiv__': '/',
    '__eq__': '=',
    '__ne__': '!=',
    '__lt__': '<',
    '__le__': '<=',
    '__gt__': '>',
    '__ge__': '>=',
}

class BindError(Exception):
    pass

# Derives the lisp name of a python function or method handle, as follows:
#
# * Python dunder names are translated to their corresponding operator or symbol
#   usind the ``dunder_names`` table.
#
# * A trailing '_p' in the Python name is converted into a question mark in the
#   lisp name.
#
# * A lone trailing '_' in the Python name stripped.
#
# * Any remaining underscores in the Python name are converted to dashes in the
#   lisp name.
#
# This only applies to named functions. Python lambdas and non-function
# callables do not have names.
def lisp_name(fn):
    name = fn.__name__
    if name == '<lambda>':
        raise BindError(f'Lambda {repr(fn)} has no name')

    # Translate operators early, and throw out the existing name
    if name in dunder_names:
        return dunder_names[name]

    # Trailing _p is a predicate, translate to ?
    if name.endswith('_p'):
        name = name[:-2] + '?'

    # Trailing _ is probably a name that conflicts with a python keyword
    if name.endswith('_') and not name.endswith('__'):
        name = name[:-1]

    # Remaining underscores are dashes
    name = name.replace('_', '-')

    return name

# Wraps a function which returns no values in a function which returns an empty
# tuple.
def wrap_void(fn):
    @wraps(fn)
    def wrapper(*args):
        fn(*args)
        return ()
    return wrapper

# Wraps a function which returns one value in a function which returns a
# one-valued tuple.
def wrap_fn(fn):
    @wraps(fn)
    def wrapper(*args):
        return fn(*args),
    return wrapper

# An Actinide registry allows its containing module to be loaded into a Session
# to provide additional functions and syntax to code run in that Session.

class Registry(object):
    def __init__(self):
        self.bindings = []
        self.macros = []
        self.evals = []

    def bind(self, name, value):
        self.bindings.append((name, value))
        return value

    def void(self, f):
        self.bind(lisp_name(f), wrap_void(f))
        return f

    def fn(self, f):
        self.bind(lisp_name(f), wrap_fn(f))
        return f

    def builtin(self, f):
        self.bind(lisp_name(f), f)
        return f

    def macro_bind(self, name, value):
        self.macros.append((name, value))
        return value

    def macro_void(self, f):
        self.macro_bind(lisp_name(f), wrap_void(f))
        return f

    def macro_fn(self, f):
        self.macro_bind(lisp_name(f), wrap_fn(f))
        return f

    def macro_builtin(self, f):
        self.macro_bind(lisp_name(f), f)
        return f

    def eval(self, source):
        self.evals.append(source)
