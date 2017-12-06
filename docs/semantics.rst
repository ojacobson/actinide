.. _semantics:

#########
Semantics
#########

.. highlight:: scheme

Forms are also the most basic unit of Actinide evaluation. Execution of an
Actinide program proceeds by *reducing* one form to a simpler result, until
only a single irreducible form is left (which is the program's result).

Most Actinide programs consist of a top-level compound form, which must be
fully reduced to run the program to completion. The following sections describe
the mechanism and results of reducing each kind of form. In general, evaluation
proceeds by reducing the inner-most, left-most unreduced form, iteratively,
until all forms have been reduced.

********
Literals
********

Literal forms reduce to themselves, unchanged. The following forms are
considered literal forms:

* Integers
* Decmials
* Strings
* Booleans

For example, the result of reducing ``1`` is ``1``.

*******
Symbols
*******

Symbols, other than those that are part of :ref:`special forms <special
forms>`, represent variables in Actinide programs, and reduce to the values of
those variables in the current *environment*.

In an environment where a symbol has a value, the reduction of that symbol is
the value it's bound to. In an environment where a symbol is not bound to any
value, the reduction of that symbol produces an error and stops the computation.

For example, in an environmet where the symbol ``x`` is bound to ``5``, the
result of reducing ``x`` is ``5``.

An Actinide program is run in an initial *top-level environment*, which comes
pre-populated with bindings for all of Actinide's built-in functions and
values, plus any values placed there by the host program. As Actinide reduces a
program, the bindings in that initial environment can change, and additional
environments may be created. The *current environment* is controlled by the
:ref:`lambda` form and by :ref:`procedure application`.

.. _special forms:

*************
Special forms
*************

Lists that begin with one of the following symbols are evaluated specially.

~~~~~
quote
~~~~~

Syntax:

.. code-block:: scheme

    (quote form)

A ``quote`` form guards another form from evaluation. The result of reducing a
quote form is exactly the guarded ``form``. This allows forms that may have
special meaning, such as lists, to be embedded in Actinide programs as literal
values, stripped of their special meaning.

.. _begin:

~~~~~
begin
~~~~~

Syntax:

.. code-block:: scheme

    (begin [form-1 ... form-n])

A ``begin`` form fully evaluates each subform in left-to-right order, then
reduces to the value of the final subform. This allows for forms with side
effects to be evaluated (and their results ignored) before evaluating a final
form that produces a result.

An empty ``begin`` form evaluates to the empty list.

Example:

.. code-block:: scheme

    (begin
        ; define a function...
        (define (f) 1)
        ; ...and call it
        (f))

.. _if:

~~
if
~~

Syntax:

.. code-block:: scheme

    (if cond if-true)
    (if cond if-true if-false)

An ``if`` form conditionally evaluates one of two forms based on the result of
a condition. The ``cond`` form is fully evaluated first; if it reduces to a
true value, then the ``if-true`` form is evaluated and the ``if`` form reduces
to its result; otherwise, the ``if-false`` form is evaluated and the ``if``
form reduces to its result. In either case, the other form is discared without
evaluation.

An ``if`` form without an ``if-false`` form reduces to nil if the ``cond`` form reduces to a false value.

The following values are false:

* the empty list
* ``#f``
* integer and decimal zeroes
* empty strings
* empty vectors

All other values are true.

Example:

.. code-block:: scheme

    (if #t 'was-true 'was-false)

    (if (goldback-conjecture)
        "Eureka!")

.. _lambda:

~~~~~~
lambda
~~~~~~

Syntax:

.. code-block:: scheme

    (lambda formals [body-1...body-n])

Defines a procedure taking arguments described by the ``formals`` form, whose
application will evaluate the ``body`` forms in order and will reduce to the
result of the last form.

The ``formals`` form must have one of the following structures:

* A list of symbols, each of which will be bound to a single argument when the
  procedure is applied, in the order listed.

* An improper list of symbols. Each symbol other than the final tail symbol
  will be bound to an argument from the procedure application; the final tail
  symbol will be bound to a list of all arguments that were not bound to any
  other symbol.

* A single symbol, which will be bound to a list of the arguments when the
  procedure is applied.

A ``lambda`` form reduces to a newly-created procedure value whose body is the
list of body forms and whose formal argument list is the formals.

Each procedure captures the environment in effect when the ``lambda`` form is
evaluated, allowing the procedure body to see variables that were visible at
that time, even if the procedure outlives the context where that environment is
defined.

Each time a procedure is applied, Actinide creates a new environment that
inherits from the captured environment and binds the values of arguments from
the procedure application to the symbols named in the procedure's ``formals``.
This is the primary mechanism for creating new environments in Actinide.
Procedure application then evaluates the body forms, in that new environment,
in left-to-right order. The result of the final form is the result of the
procedure application. (In fact, procedures whose bodies consist of multiple
forms, or of no forms at all, are converted to a procedure whose body is a
single ``begin`` form.)

Examples:

.. code-block:: scheme

    ; Creates a constant function of zero arguments, which always
    ; evaluates to 1.
    (lambda () 1)

    ; Defines a variable in the current environment (as discussed
    ; below), then creates a function of zero arguments that returns
    ; that variable. Initially, it will always return 5, but if the
    ; value of x is changed in the outer environment, the function's
    ; return value will change as well.
    (begin
        (define x 5)
        (lambda () x))

    ; Defines a function of two arguments, a and b, whose result is
    ; the sum of those arguments. This is a simple alias for the +
    ; built-in function, illustrating the idea that functions can
    ; call other functions.
    (lambda (a b) (+ a b))

    ; Defines a function that takes one or more arguments, with the
    ; first argument bound to a (and ignored) and the list of
    ; remaining arguments bound to b. This always returns b
    ; unchanged, and throws away a.
    (lambda (a . b) b)

    ; Defines a function that takes any number of arguments, and
    ; returns them as a list. This is a simple alias for the list
    ; built-in function.
    (lambda a a)

.. _define:

~~~~~~
define
~~~~~~

Syntax:

.. code-block:: scheme

    (define symb form)
    (define signature [body-1...body-n])

A define form creates a new variable in the current environment, and binds a
value to that variable. There are two variations on this form: simple
definition and procedure definition.

In the first form, the ``symb`` subform must be a single symbol. The ``form``
subform is fully reduced, and the resulting value is bound to the variable
``symb`` in the current environment. For example:

.. code-block:: scheme

    (begin
        ; Defines a variable, x, whose initial value is 5.
        (define x 5)
        ; Evaluates to the value of x.
        x)

In the second, the ``signature`` subform must be a procedure signature: a list
or improper list of symbols. The first element of that list is the name the
procedure will be bound to, while the rest of that list is treated as the
``formals`` form as described under :ref:`lambda`. The list of ``body`` forms become
the resulting procedure's body, as usual.

Under the hood, the second form is translated into the first automatically -
the form

.. code-block:: scheme

    (define (sum a b) (+ a b))

is exactly equivalent to the form

.. code-block:: scheme

    (define sum
            (lambda (a b) (+ a b)))

However, when the option is available, procedure definition should be preferred
as it's generally more readable.

~~~~~~
values
~~~~~~

Syntax:

.. code-block:: scheme

    (values [body-1...body-n])

Where most forms reduce to a single value, the ``values`` form reduces to a
sequence of values, in place. This allows a function or any other form to
reduce to multiple distinct values, which can be inserted into other forms.

The body forms are evaluated left-to-right, and the ``values`` form reduces to
the resulting values, left-to-right.

Example:

.. code-block:: scheme

    (begin
        ; A function which returns two values, both equal to its
        ; sole argument
        (define (two x) (values x x))
        ; = accepts two values and compares them.
        (= (two 53)))

.. _define-macro:

~~~~~~~~~~~~
define-macro
~~~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (define-macro symb form)
    (define-macro signature [body-1...body-n])

A ``define-macro`` form creates a new :ref:`macro transformer <macros>`
function in the current environment's macro table. This is identical to the
:ref:`define` form, but the resulting binding is not visible as a variable, and
affects macro expansion of Actinide programs. Macro bindings using the first
form must bind the symbol to a procedure or built-in function producing exactly
one result.

.. warning::

    A ``define-macro`` form which appears within a procedure body will create a
    macro in the environment created when the procedure is applied. These
    macros are **never** visible to the macro expander, and will have no effect.

.. _procedure application:

*********************
Procedure application
*********************

Any list which is not empty, and not a :ref:`special form <special forms>`, is
a procedure application, applying either a built-in procedure (provided by
Actinide or by the host program) or a procedure defined using the :ref:`lambda`
special form or any of its :ref:`equivalents <define>`.

Syntax:

.. code-block:: scheme

    (fn [arg-1...arg-n])

The subforms of a list form are evaluated from left to right. The ``fn``
subform must evaluate to a procedure; the remaining ``body`` forms are
evaluated to produce the values of arguments to that procedure. Once all of the
subforms have been evaluated, the procedure is applied to its arguments, and
the procedure application itself reduces to the result of the applied procedure.

During the application of a procedure,

1. A new *child* environment is created from the procedure's captured
    environment. In this environment, any name not defined in the child
    environment is looked up in the captured environment instead.

2. The values of the arguments from the function application form are bound to
    the names given by the procedure's formal arguments list.

3. The procedure's body forms are evaluated from left to right in the child
    environment.

4. The result of the last form in the procedure body is used as the result of
    the function application.

~~~~~~~~~~~~~~~~~~~
Loops and Recursion
~~~~~~~~~~~~~~~~~~~

Actinide has no primitives dedicated to repeating parts of a program. To loop,
a procedure must recurse. Actinide guarantees that recursion in *tail position*
can proceed arbitrarily far without exhausting any resources solely due to the
number of recursive calls. Actinide guarantees tail recursion.

The following forms are considered to be in tail position:

* The final form of a :ref:`procedure body <lambda>` is in tail position with
  respect to the application of that procedure.

* The final form of a :ref:`begin` form is in tail position with respect to the
  ``begin`` form itself.

* The ``if-true`` form of an :ref:`if` form whose condition is true, and the
  ``if-false`` form of an ``if`` form whose condition is not true, is in tail
  position with respect to the ``if`` form.

* If a form is in tail position with respect to another form, it is also in
  tail position for any form that form is in the tail position of, and so on
  outwards until the form is either in tail position with respect to the root
  of the program or a form is found for which the containing form is not in
  tail position.

As an example, the following implementation of the factorial algorithm is
recursive, but the recursion does not appear in tail position (it is not *tail
recursive*):

.. code-block:: scheme

    (define (factorial n)
            (if (= n 1)
                1
                (* n (factorial (- n 1)))))

The ``factorial`` function *is not* called in tail position with respect to the
body of the ``factorial`` function: After reducing the inner application of
``factorial``, the reduction of the outer ``factorial`` application must
continue so that it can apply the ``*`` function to the result.

Attempting to evaluate ``(factorial 1000)`` fails due to limits on call depth:
``maximum recursion depth exceeded while calling a Python object``

.. note::

    This warning leaks some implementation details, obviously. The exact
    failure mode should not be relied on; the key property is that
    deeply-recursive programs will raise an error when they exhaust the
    implementation's resources.

The following implementation of the factorial algorithm *is* tail-recursive:

.. code-block:: scheme

    (define (fact n a)
            (if (= n 1)
                a
                (fact (- n 1) (* n a))))

The ``fact`` function is called in tail position with respect to the body of
``fact``. Specifically, it is in tail position with respect to the ``if`` form
whenever ``n`` is not equal to ``1``, and the ``if`` form is in tail position
with respect to the body of the ``fact`` function.

Evaluating ``(fact 1000 1)`` correctly computes the factorial of ``1000`` on
any machine with enough memory to store the result.
