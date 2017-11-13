# ## EXPANDER

from .types import *

# Expand and syntax-check a form.
#
# This replaces shorthand notations, such as ``(define (a b c) body)``, with
# their longhand equivalents (``(define a (lambda (b c) body)))``).
#
# Because this deals with unevaluated programs, this algorithm can safely
# recurse: the input depth simply isn't that large.
def expand(form, symbols):
    if nil_p(form) or not list_p(form):
        return form
    # huge cheat. Working with python lists is hugely easier for this than
    # working with conses, and it's after midnight. Flatten the form, expand it,
    # and reconstitute it. This incurs two bonus copies per form: suck it up.
    symb, *args = flatten(form)
    if symb == symbols['if'] and len(args) == 2:
        args.append(None)
    elif symb == symbols['define']:
        decl, *body = args
        if list_p(decl):
            decl = flatten(decl)
            name, *formals = decl
            lambda_ = list(symbols['lambda'], list(*formals), *body)
            args = [name, lambda_]
    elif symb == symbols['lambda']:
        formals, *body = args
        if len(body) != 1:
            body = [list(symbols['begin'], *body)]
        args = [formals, *body]
    form = list(expand(symb), *[expand(subform, symbols) for subform in args])
    return form
