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
    '__ge__': '>',
}

# Derives the lisp name of a python function or method handle, as follows:
#
# * Python dunder names are translated to their corresponding operator or
#   symbol usind the ``dunder_names`` table.
#
# * A trailing '_p' in the Python name is converted into a question mark in the
#   lisp name.
#
# * Any remaining underscores in the Python name are converted to dashes in the
#   lisp name.
#
# This only applies to named functions. Python lambdas and non-function
# callables do not have names.
def lisp_name(fn):
    name = fn.__name__
    if name == '<lambda>':
        return None

    if name in dunder_names:
        return dunder_names[name]

    # Trailing _p is a predicate, translate to ?
    if name.endswith('_p'):
        name = name[:-2] + '?'

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

def make_registry():
    bindings = []
    voids = []
    fns = []
    builtins = []

    def bind(name, val):
        bindings.append((name, val))
        return val

    def void(f):
        voids.append(f)
        return f

    def fn(f):
        fns.append(f)
        return f

    def builtin(f):
        builtins.append(f)
        return f

    return bindings, voids, fns, builtins, bind, void, fn, builtin
