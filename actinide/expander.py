# ## EXPANDER

from .types import *

# Raised if expansion of a form fails.
class ExpansionError(Exception):
    pass

# Expand and syntax-check a form.
#
# This replaces shorthand notations, such as ``(define (a b c) body)``, with
# their longhand equivalents (``(define a (lambda (b c) body)))``).
#
# Because this deals with unevaluated programs, this algorithm can safely
# recurse: the input depth simply isn't that large.
def expand(form, symbols, macros):
    if nil_p(form) or not cons_p(form):
        return form
    if head(form) == symbols['quote']:
        return form
    if head(form) == symbols['if']:
        form = expand_if(form)
    elif head(form) == symbols['define']:
        form = expand_define(form, symbols)
    elif head(form) == symbols['define-macro']:
        form = expand_define(form, symbols)
    elif head(form) == symbols['lambda']:
        form = expand_lambda(form, symbols)
    elif head(form) == symbols['quasiquote']:
        form = expand_quasiquote(form, symbols)
    elif symbol_p(head(form)) and head(form) in macros:
        form = expand_macro(form, symbols, macros)
    form = expand_subforms(form, symbols, macros)
    return form

# Recursively expand subforms in an already-expanded top-level form.
def expand_subforms(list, symbols, macros):
    if nil_p(list):
        return nil
    if not cons_p(list):
        return list
    head, tail = uncons(list)
    return cons(
        expand(head, symbols, macros),
        expand_subforms(tail, symbols, macros),
    )

# Expand an `if` form.
#
# (if COND TRUE)
#   => (if COND TRUE nil)
def expand_if(form):
    head, form = uncons(form)
    cond, form = uncons(form)
    true, form = uncons(form)
    if nil_p(form):
        return list(head, cond, true, None)
    false, form = uncons(form)
    return list(head, cond, true, false)

# Expand a define or define-macro form.
#
# (define (NAME FORMALS) BODY)
#   => (define name (lambda FORMALS BODY))
def expand_define(form, symbols):
    head, form = uncons(form)
    symb, form = uncons(form)
    if cons_p(symb):
        return expand_lambda_define(head, symb, form, symbols)
    val, form = uncons(form)
    return list(head, symb, val)

def expand_lambda_define(head, symb, body, symbols):
    name, formals = uncons(symb)
    return list(head, name, cons(symbols['lambda'], cons(formals, body)))

# Expands a lambda.
#
# (lambda FORMALS FORM)
#   => unchanged
# (lambda FORMALS)
#   => (lambda FORMALS (begin))
# (lambda FORMALS FORM ...FORMS)
#   => (lambda FORMALS (begin FORM ...FORMS))
def expand_lambda(form, symbols):
    head, form = uncons(form)
    formals, form = uncons(form)
    # XXX check formals
    if cons_p(form) and not nil_p(tail(form)):
        form = list(cons(symbols['begin'], form))
    return cons(head, cons(formals, form))

# Expands a quasiquote, recursively, expanding unquotes as needed.
def expand_quasiquote(form, symbols):
    head, form = uncons(form)
    body, form = uncons(form)
    return expand_quasiquoted(body, symbols)

def expand_quasiquoted(form, symbols):
    if nil_p(form):
        return form
    if not cons_p(form):
        return list(symbols['quote'], form)
    first, rest = uncons(form)
    if first == symbols['unquote']:
        next, rest = uncons(rest)
        return next
    if not nil_p(first) and cons_p(first):
        candidate, body = uncons(first)
        if candidate == symbols['unquote-splicing']:
            next, unquote_next = uncons(body)
            return list(
                symbols['append'],
                next,
                expand_quasiquoted(rest, symbols),
            )
    return list(
        symbols['cons'],
        expand_quasiquoted(first, symbols),
        expand_quasiquoted(rest, symbols),
    )

# Expands macro definitions, iterating until no further expansion is possible.
def expand_macro(form, symbols, macros):
    macro, args = uncons(form)
    macro_body = macros[macro]
    args = flatten(args)
    expansion, = macro_body(*args)
    return expand(expansion, symbols, macros)
