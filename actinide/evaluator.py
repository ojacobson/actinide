from .environment import *

# Circular import. Hard to avoid: `eval` calls `lambda_`, `lambda_` eventually
# calls `Procedure`, and `Procedure` calls `eval`. We indirect the call through
# the module object to avoid problems with import order.
from . import types as t

# ## EVALUATION
#
# The following system implements a continuation-passing interpreter for
# Actinide. It is heavily inspired by the redex/continuation system described in
# <https://docs.racket-lang.org/reference/eval-model.html> for the Racket
# language.
#
# The call stack of an Actinide program is implemented as a chain of
# continuation functions, which grows and shrinks as evaluation proceeds.
# Because the evaluator itself is tail-recursive, tail calls are free in
# Actinide - they do not cause the call stack to grow.
#
# In principle, this could expose ``call/cc``, but the need for that primitive
# hasn't come up.
#
# Evaluating a form in this system requires both an environment (from the
# ``environment`` module) and a symbol table (from the ``symbol_table`` module).
# Callers are encouraged to use the ``Session`` system exposed in the root of
# this package, instead of calling the invoker directly: a session manages these
# resources automaticallty. The more intrepid user can manually compile an
# arbitrary expression using the ``eval`` continuation factory, described below.
#
# If the interpreter encounters an error during evaluation, the resulting Python
# exception bubbles up out of the interpreter and destroys the state of the
# computation.

# Reduce a continuation to its final value.
#
# This iteratively calls the current continuation with the current arguments
# until the current continuation is None, then exits, returning the final
# arguments.
#
# This trampoline exists to deal with the absence of tail call optimizations in
# Python. By returning the next continuation rather than invoking it, we avoid
# growing the Python call stack without bound.
#
# The result of evaluating a continuation is always a Python tuple. For
# expressions, this tuple contains the value(s) produced by the expression. For
# forms which do not produce a value, this returns the empty tuple.
def run(continuation, args=()):
    while continuation is not None:
        continuation, args = continuation(*args)
    return args

# ## FLAT CONTINUATIONS
#
# These continuation factories and transformers produce continuations which
# receive already-evaluated values, and which produce evaluated results.

# Returns a continuation which yields a single value, verbatim, and chains to a
# known target continuation. This implements evaluation for literals.
def literal(value, continuation):
    return lambda: (continuation, (value,))

# Returns a continuation which looks up a symbol in an environment, yields the
# result, and chains to a known target continuation. This implements evaluation
# for variable lookups.
def symbol(symb, environment, continuation):
    return lambda: (continuation, (environment.find(symb),))

# Returns a continuation which yields a newly-created procedure, and chains to a
# known target continuation. This implements evaluation for the tail of a lambda
# form. (The head of the lambda form must be discarded before calling this
# factory.)
def lambda_(defn, environment, symbols, continuation):
    formals = t.flatten(t.head(defn))
    body = t.head(t.tail(defn))
    proc = t.Procedure(body, formals, environment, symbols)
    return lambda: (continuation, (proc,))

# Returns a continuation which takes a value and binds that value to a symbol in
# a specific environment, then chains to a known target continuation. This
# implements evaluation of the `define` special form, once the value is known.
def bind(symbol, environment, continuation):
    def bind_(value):
        environment.define(symbol, value)
        return (continuation, ())
    return bind_

# Returns a continuation which takes a value and returns one of two known target
# continuations based on the value. If the value is true (Python truthy), this
# chains to the `on_true` continuation. If the value is not true (Python falsy),
# this chains to the `on_false` continuation. In either case, the continuation
# not chained to is discarded.
def branch(on_true, on_false):
    return lambda val: (on_true if val else on_false, ())

# Returns a continuation which receives values, and appends them to the values
# passed to this factory, before chaining to a known target continuation. This
# implements intermediate evaluation of list forms, where part of the list is
# already known, as well as splicing for forms that yield multiple values.
def append(args, continuation):
    return lambda *tail: (continuation, (*args, *tail))

# Transforms a continuation which should receive function results into a
# function call continuation. A function call continuation receives a function
# and a sequence of arguments. If the function is a primitive function, the
# reduction directly calls the function and chains to the wrapped continuation.
# If the function is a procedure, this instead returns a continuation which will
# invoke the procedure, then chain to the wrapped continuation.
def invoke(continuation):
    def invoke_(fn, *args):
        if isinstance(fn, t.Procedure):
            return procedure_call(fn, *args)
        return builtin(fn, *args)

    def procedure_call(fn, *args):
        call_env = fn.invocation_environment(*args)
        call_cont = fn.continuation(call_env, continuation)
        return (call_cont, ())

    def builtin(fn, *args):
        result = fn(*args)
        return (continuation, result)
    return invoke_

# ## RECURSIVE CONTINUATIONS
#
# The following continuation factories recurse, producing complex chains of
# continuations.

# Returns a continuation which, when invoked, evaluates the first step of a form
# and chains to a continuation for the remainder of the form. When the form is
# exhausted, the final continuation chains to a known target continuation.
#
# This is the heart of the continuation-passing transformation. Every valid form
# can be translated into continuation-passing form throught this factory. This
# handles literals, symbols, special forms, and function application.
def eval(value, environment, symbols, continuation):
    if t.symbol_p(value):
        return symbol(value, environment, continuation)
    if t.nil_p(value) or not t.list_p(value):
        return literal(value, continuation)
    # Special forms (all of which begin with a special symbol, discarded here)
    if t.head(value) == symbols['if']:
        return if_(t.tail(value), environment, symbols, continuation)
    if t.head(value) == symbols['define']:
        return define(t.tail(value), environment, symbols, continuation)
    if t.head(value) == symbols['lambda']:
        return lambda_(t.tail(value), environment, symbols, continuation)
    # Ran out of alternatives, must be a function application
    return apply(value, environment, symbols, invoke(continuation))

# Returns a continuation which fully evaluates a `(define symbol expr)` form,
# before chaining to a known target continuation. First, the returned
# continuation evaluates the `expr` (recursively, using `eval` to construct the
# continuation`. The result of this evaluation is chained to a `bind`
# continuation, to store the result of evaluation in the target environment.
# Finally, the `bind` continuation chains to the target continuation.
def define(value, environment, symbols, continuation):
    symb, expr = t.flatten(value)

    if not t.symbol_p(symb):
        raise RuntimeError("Argument to define not a symbol: {t.display(symb)}")

    bind_cont = bind(symb, environment, continuation)
    eval_cont = eval(expr, environment, symbols, bind_cont)
    return lambda: (eval_cont, ())

# Returns a continuation which fully evaluates an `(if cond if-true if-false)`
# form, before chaining to a known target continuation. First, the returned
# continuation evaluates the `cond` expression (recursively, using `eval` to
# construct the continuation), which chains to a `branch` continuation
# containing continuations for the `if-true` and `if-false` epxressions. The
# `if-true` and `if-false` continuations each chain to the target continuation.
def if_(value, environment, symbols, continuation):
    cond, if_true, if_false = t.flatten(value)

    if_true_cont = eval(if_true, environment, symbols, continuation)
    if_false_cont = eval(if_false, environment, symbols, continuation)
    branch_cont = branch(if_true_cont, if_false_cont)

    return eval(cond, environment, symbols, branch_cont)

# Returns a continuation which fully evaluates the elements of a list, before
# chaining to a target continuation. If this is applied to an empty list, the
# returned continuation accepts arbitrary arguments and chains to the target
# continuation with those arguments. Otherwise, this evaluates the head of the
# list (recursively, using `eval` to prepare the continuation), then chains to
# an `append` continuation to glue the result onto the result of recursively
# calling `apply` on the tail of the list.
def apply(list, environment, symbols, continuation):
    if t.nil_p(list):
        return lambda *args: (continuation, args)
    tail_cont = apply(t.tail(list), environment, symbols, continuation)
    return lambda *args: (eval(t.head(list), environment, symbols, append(args, tail_cont)), ())
