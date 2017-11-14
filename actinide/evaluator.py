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
def run(continuation, environment, args=()):
    while continuation is not None:
        continuation, environment, *args = continuation(environment, *args)
    return args

# ## FLAT CONTINUATIONS
#
# These continuation factories and transformers produce continuations which
# receive already-evaluated values, and which produce evaluated results.

# Returns a continuation which yields a single value, verbatim, and chains to a
# known target continuation. This implements evaluation for literals.
def literal(value, continuation):
    return lambda environment: (continuation, environment, value)

# Returns a continuation which looks up a symbol in an environment, yields the
# result, and chains to a known target continuation. This implements evaluation
# for variable lookups.
def symbol(symb, continuation):
    return lambda environment: (continuation, environment, environment.find(symb))

# Returns a continuation which yields a newly-created procedure, and chains to a
# known target continuation. This implements evaluation for the tail of a lambda
# form. (The head of the lambda form must be discarded before calling this
# factory.)
def lambda_(defn, symbols, continuation):
    formals = t.flatten(t.head(defn))
    body = t.head(t.tail(defn))
    def lambda__(environment):
        proc = t.Procedure(body, formals, environment, symbols)
        return (continuation, environment, proc)
    return lambda__

# Returns a continuation which takes a value and binds that value to a symbol in
# a specific environment, then chains to a known target continuation. This
# implements evaluation of the `define` special form, once the value is known.
def bind(symbol, continuation):
    def bind_(environment, value):
        environment.define(symbol, value)
        return (continuation, environment)
    return bind_

# Returns a continuation which takes a value and returns one of two known target
# continuations based on the value. If the value is true (Python truthy), this
# chains to the `on_true` continuation. If the value is not true (Python falsy),
# this chains to the `on_false` continuation. In either case, the continuation
# not chained to is discarded.
def branch(on_true, on_false):
    return lambda environment, val: (on_true if val else on_false, environment)

# Returns a continuation which receives values, and appends them to the values
# passed to this factory, before chaining to a known target continuation. This
# implements intermediate evaluation of list forms, where part of the list is
# already known, as well as splicing for forms that yield multiple values.
def append(args, continuation):
    return lambda environment, *tail: (continuation, environment, *args, *tail)

def begin(continuation):
    return lambda environment, *args: (continuation, environment, *(args[-1:] if args else ()))

# Transforms a continuation which should receive function results into a
# function call continuation. A function call continuation receives a function
# and a sequence of arguments. If the function is a primitive function, the
# reduction directly calls the function and chains to the wrapped continuation.
# If the function is a procedure, this instead returns a continuation which will
# invoke the procedure, then chain to the wrapped continuation.
def invoke(continuation):
    def invoke_(environment, fn, *args):
        if isinstance(fn, t.Procedure):
            return procedure_call(environment, fn, *args)
        return builtin(environment, fn, *args)

    def procedure_call(environment, fn, *args):
        call_env = fn.invocation_environment(*args)
        call_cont = fn.continuation
        return_cont = tail_graft(continuation, environment, call_cont)
        return (return_cont, call_env)

    def builtin(environment, fn, *args):
        result = fn(*args)
        return (continuation, environment, *result)
    return invoke_

# Continuation transformer. Given a guarded continuation, and a graft
# continuation and environment, if the graft continuation is None then this
# returns the guarded continuation unchanged. Otherwise, this replaces the
# guarded continuation with a guard.
#
# The guard calls guarded continuation when applied, but if the guarded
# continuation chains to None, the guard replaces the returned continuation and
# environment with the graft continuation and environment. This handles
# environment restoration after a function call.
def tail_graft(continuation, environment, guarded):
    # Tail call magic: if we're not going to transition to another continuation,
    # don't bother grafting environment recovery on.
    if continuation is None:
        return guarded

    def guard(env, *args):
        next, env, *args = guarded(env, *args)
        if next is None:
            return (continuation, environment, *args)
        return (tail_graft(continuation, environment, next), env, *args)

    return guard

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
def eval(value, symbols, continuation):
    if t.symbol_p(value):
        return symbol(value, continuation)
    if t.nil_p(value) or not t.list_p(value):
        return literal(value, continuation)
    # Special forms (all of which begin with a special symbol, discarded here)
    if t.head(value) == symbols['if']:
        return if_(t.tail(value), symbols, continuation)
    if t.head(value) == symbols['define']:
        return define(t.tail(value), symbols, continuation)
    if t.head(value) == symbols['lambda']:
        return lambda_(t.tail(value), symbols, continuation)
    if t.head(value) == symbols['begin']:
        return apply(t.tail(value), symbols, begin(continuation))
    # Ran out of alternatives, must be a function application
    return apply(value, symbols, invoke(continuation))

# Returns a continuation which fully evaluates a `(define symbol expr)` form,
# before chaining to a known target continuation. First, the returned
# continuation evaluates the `expr` (recursively, using `eval` to construct the
# continuation`. The result of this evaluation is chained to a `bind`
# continuation, to store the result of evaluation in the target environment.
# Finally, the `bind` continuation chains to the target continuation.
def define(value, symbols, continuation):
    symb, expr = t.flatten(value)

    if not t.symbol_p(symb):
        raise RuntimeError("Argument to define not a symbol: {t.display(symb)}")

    bind_cont = bind(symb, continuation)
    eval_cont = eval(expr, symbols, bind_cont)
    return lambda environment: (eval_cont, environment)

# Returns a continuation which fully evaluates an `(if cond if-true if-false)`
# form, before chaining to a known target continuation. First, the returned
# continuation evaluates the `cond` expression (recursively, using `eval` to
# construct the continuation), which chains to a `branch` continuation
# containing continuations for the `if-true` and `if-false` epxressions. The
# `if-true` and `if-false` continuations each chain to the target continuation.
def if_(value, symbols, continuation):
    cond, if_true, if_false = t.flatten(value)

    if_true_cont = eval(if_true, symbols, continuation)
    if_false_cont = eval(if_false, symbols, continuation)
    branch_cont = branch(if_true_cont, if_false_cont)

    return eval(cond, symbols, branch_cont)

# Returns a continuation which fully evaluates the elements of a list, before
# chaining to a target continuation. If this is applied to an empty list, the
# returned continuation accepts arbitrary arguments and chains to the target
# continuation with those arguments. Otherwise, this evaluates the head of the
# list (recursively, using `eval` to prepare the continuation), then chains to
# an `append` continuation to glue the result onto the result of recursively
# calling `apply` on the tail of the list.
def apply(list, symbols, continuation):
    if t.nil_p(list):
        return lambda environment, *args: (continuation, environment, *args)
    tail_cont = apply(t.tail(list), symbols, continuation)
    return lambda environment, *args: (
        eval(t.head(list), symbols, append(args, tail_cont)),
        environment,
    )
