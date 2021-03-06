.. _macros:

######
Macros
######

This section describes Actinide's macro facility, which transforms programs
between parsing and evaluation. Macros provide a powerful way to extend Actinide's syntax.

.. warning::

    Actinide's macro expansion facility is broadly inspired by Common Lisp's,
    and implements *non-hygienic* macros: symbols generated by macro expansion
    can conflict with symbols defined in the context where the macro is
    expanded in both directions.

    I would like to replace this with a macro expander based on Scheme's, but I
    can't promise that I'll ever get around to it. Writing macros using
    Actinide's macro system is fraught with minor but irritating problems
    related to symbol capture, and macros should use user-provided symbols as
    much as possible to avoid interacting with the environment at the expansion
    site.

.. warning::

    Macro expansion is fully completed before any evaluation occurs. Programs
    can define macros for future programs run in the same environment to use,
    but not for themselves. The following does not expand the "remove-one"
    macro:

    .. code-block:: scheme

        (begin
            (define-macro (remove-one a b) b)
            (remove-one 1 2))

    Instead, that program attempts to evaluate an undefined ``remove-one``
    function as an ordinary procedure, and fails. The macro binding introduced
    in this program would be available to future programs run in the same
    environment.

    The Actinide REPL runs each form as an independent program, so
    interactively defining macros in the REPL behaves in an intuitive way.
    Programs that embed Actinide must take care to provide sensible ways to
    load macro definitions, as well as any supporting functions those macro
    definitions require. The embedding guide's ``An.eval`` primitive is the
    recommended way to pre-load definitions into a session, as each ``eval``
    binding is run as an independent program, sharing a top-level environment
    with future programs run in the same session.

The :ref:`define-macro` form, introduced in the :ref:`semantics` chapter,
creates macro transformer bindings. In brief, a *macro transformer* is an
ordinary Actinide procedure, whose result is an unevaluated *form*, rather than
a value. The arguments to a macro transformer are also forms, which the macro
transformer can pick apart and manipulate.

When Actinide's expansion step encounters a list form whose head is a symbol
matching a macro transformer in the top-level environment, the form is removed
from the program. The head is discarded (it only identifies the macro), and the
remaining subforms are passed, un-evaluated, to the macro transformer as
arguments. The result of the macro transformer is inserted into the program in
place of the removed macro form.

The following example illustrates, by defining a new ``let-one`` special form. This special form has the following syntax:

.. code-block:: scheme

    (let-one (name form) body)

When it's reduced, it creates a new environment in which the result of reducing
``form`` is bound to the variable ``name``, then evaluates ``body`` in that
environment.

.. code-block:: scheme

    (define-macro (let-one binding body)
        (begin
            (define name (head binding))
            (define val (head (tail binding)))
            `((lambda (,name) ,body) ,val))))

To use this macro, apply it as if it were a function:

.. code-block:: scheme

    (let-one (x 1) (+ x 2))

The macro transformer receives the forms ``(x 1)`` and ``x``, unevaluated, as
arguments, and substitutes them into a :ref:`quasiquoted <quasiquotes>` form,
which is used as a template for the result of the macro. The three *unquoted*
parts (``,name``, ``,body``, and ``val``) are replaced by evaluating the
symbols in the context of the macro procedure, and expand to the relevant parts
of the input forms.

The returned form is equivalent to

.. code-block:: scheme

  ((lambda (x) (+ x 2) 1)

This program evaluates to 3, without binding ``x`` in the current environment.

.. _quasiquotes:

~~~~~~~~~~~
Quasiquotes
~~~~~~~~~~~

Actinide provides three quote-like special forms which are fully handled by the
macro expander, and which are meant to ease the development of macros.

quasiquote
~~~~~~~~~~

Syntax:

.. code-block:: scheme

    `form
    (quasiquote form)

Evaluation of a quasiquote form produces an expression that reconstructs
``form``. If ``form`` contains no ``unquote`` or ``unquote-splicing`` forms,
then ```form`` produces a form which evaluates to the equivalent of ``'form``.

The exact expansion of quasiquote forms produces expressions which, when
evaluated, produce equivalents to simpler quoted forms. However, the exact
result of a quasiquoted form is generally a form which, when evaluated, calls a
sequence of built-in procedures to construct lists, rather than the lists
themselves. For example, the form ```(+ 1 2)`` ultimately expands to

.. code-block:: scheme

    (cons '+ (cons '1 (cons '2 '())))

which evaluates to ``'(+ 1 2)``, rather than expanding to ``'(+ 1 2)`` directly.

unquote
~~~~~~~

Syntax:

.. code-block:: scheme

    ,form
    (unquote form)

This form *must* appear within a ``quasiquote`` form. When the containing
``quasiquote`` form is expanded, the unquoted form is placed in the result
without quoting, so that it will be evaluated normally when the quasiquote form
is evaluated. The result of evaluating ``form`` will be inserted into the
result of the ``quasiquote`` form in place of the ``unquote`` form.

Example:

.. code-block:: scheme

    (begin
        (define x 5)
        `(+ ,x y))

This evaluates to a form equivalent to

.. code-block:: scheme

    '(+ 5 y)

unquote-splicing
~~~~~~~~~~~~~~~~

Syntax:

.. code-block:: scheme

    ,@form
    (unquote-splicing form)

This form *must* appear within a ``quasiquote`` form. When the containing
``quasiquote`` form is expanded, each form guarded by an ``unquote-splicing``
form will be inserted unquoted. The guarded form must evaluate to a list, which
is spliced into the ``quasiquote`` form's result. For example, given

.. code-block:: scheme

    (define x (list 1 2))

then these forms

.. code-block:: scheme

    ; unquote
    `(+ ,x)
    ; unquote-splicing
    `(+ ,@x)

expand to, respectively, forms equivalent to

.. code-block:: scheme

    ; unquote
    '(+ '(1 2))
    ; unquote-splicing
    '(+ 1 2)
