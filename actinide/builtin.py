# ## Tools for binding Python functions into a lisp environment.

from functools import wraps

# Derives the lisp name of a python function or method handle, as follows:
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
