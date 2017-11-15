#################################
The Actinide Programming Language
#################################

*****
Forms
*****

* The basic unit of Actinide syntax.

* The basic unit of Actinide evaluation.

* A program is evaluated by *reducing* forms to produce a final value, applying
  side effects during the reduction.

* What does a form look like?

    * Simple forms: literals (and intro to types)

        * Integers: an optional leading - sign for negative numbers, followed by a
          sequence of digits and underscores. Represent base-ten values with no
          fractional part. Examples: ``10``, ``-2_049``.

        * Decimals: an optional leading - sign for negative numbers, followed
          by a sequence of digits and underscores, followed by a dot, followed
          by a sequence of digits and underscores. Represent base-ten values
          which may have a factional part. Examples: ``10.0``, ``-2_049.501_2``.

        * Strings: any sequence of characters other than ``"`` or ``\``,
          enclosed in matching ``"`` marks. The sequences ``\"`` and ``\\`` are
          "escape" sequences, representing a ``"`` or ``\`` character
          respectively. Examples: ``"Hello, world."``, ``"😡💩🚀"``, ``"Quoth
          the raven, \"Four Oh Four.\""``.

        * Booleans: the special values meaning "true" and "false." Preferred
          for boolean logic operations. They are ``#t`` for true, and ``#f``
          for false.

    * Simple forms: symbols

        * Sequences of letters, numbers, and symbols not surrounded by quotes,
          and which are not themselves integers, decimals, or booleans.

        * Represent variables and constants in the program's source.

        * Evaluation of variables is covered later in this document.

        * Examples: ``hello``, ``+``, ``my-🚀``.

    * Special mention: comments

        * Cannot appear *inside* a string.

        * Starts with a ``;``, continues to the end of the line.

        * Dropped from the program entirely.

        * Examples: ``; this function is extremely spicy.``

* Compound forms: lists

    * An opening ``(``, followed by a sequence of "subforms" separated by
      spaces, followed by a closing ``)``.

    * Subforms may be any form, including another list.

    * Represent function application as well as special

* Compound forms: quotes, quasiquotes, and unqoute forms.

    * The forms ``'``, `````, ``,``, and ``,@`` represent "quote" forms.

    * These are discussed in detail in the Macros section, later on.

**********
Evaluation
**********

* When an Actinide program is run, its top-level form is evaluated.

* Evaluation of a form *reduces* the form to a simpler form - ideally, into a
  list of atomic values.

* Every kind of form can be evaluated.


******************
Simple Expressions
******************

* Evaluation of literals:

    * Integers, decimals, strings, booleans evaluate to themselves. The number
      ``1`` or the string ``"Hello, world"`` cannot be reduced any further.

* Evaluation of symbols:

    * The symbol is replaced by a value from the current *environment*.

    * This is analogous to variable expansion in other languages.

    * How do environments get their values? Defines and function application,
      covered below.

    * Certain symbols are *built in* and are automatically given values in the
      top-level environment before the program starts.

********************
Function Application
********************

* Evaluation of lists:

    * A list that starts with the symbols ``begin``, ``values``, ``if``,
      ``lambda``, ``define``, ``define-macro``, or ``quote`` is a *special
      form*, which are covered separately.

    * Any other list represents a function application.

* The subforms representing the list elements are evaluated first, left to
  right.

* If the first subform evaluates to a procedure

* During application:

    * A new *child* environment is created, with the names of the arguments
      bound to the values from the function application expression. The
      environment captured by the procedure is the *parent* of this new
      environment: any name not found in the *child* environment will be looked
      up in the parent environment instead.

    * The body of the function is run as a program, in the newly-created
      environment.

    * The result of the last form in the function is the result of the function
      application.

*************
Special Forms
*************

Lists that begin with one of the following symbols are evaluated specially.

* ``begin``: A ``begin`` form evaluates a sequence of subforms, reducing to the
  result of the last subform in the sequence. Example:

    ::

        (begin
            ; define a function...
            (define (f) 1)
            ; ...and call it
            (f))

    The forms whose results are discarded are still evaluated for their side
    effects.

* ``values``: A ``values`` form evaluates a sequence of subforms, then reduces
  to those values in the context of the containing form. This allows functions
  to return multiple values. Example:

    ::

        (begin
            (define (two x) (values x x))
            (= (two 53)))

    The ``two`` function returns two values, which are placed in the argument
    positions for the ``=`` function. This program reduces to ``#t`` if run,
    and defines ``two`` as a side effect.

* ``if``: An ``if`` form must include a ``cond`` subform producing exactly one
  value, and either one or two consequent subforms (named ``true`` and
  ``false`` subforms in this document).

      * The ``if`` form first evaluates the ``cond`` subform.

      * If it evaluates to a true value (``#t``, a non-zero integer, a non-zero
        decimal, a non-empty string, or a non-nil ``cons``), then the ``if``
        form evaluates the ``true`` subform.

      * If the ``cond`` subform evaluates to a false value (any other value),
        then the ``if`` form evaluates the ``false`` subform.

      * If the ``if`` form does not have a ``false`` subform, the ``if`` form
        evaluates to ``nil`` when the ``cond`` subform evaluates to a false
        value.

     * Examples: ``(if #t 1)`` (always equal to ``1``), ``(if some-var "okay"
       "failure")``.

* ``lambda``: A ``lambda`` form defines a procedure, and evaluates to a
  procedure value which can be used to apply the newly-defined procedure.

    * Must include a ``formals`` subform, which is generally a list of argument
      names (as symbols).

    * May include a sequence of body subforms, which are evaluated in order (as
      if by ``begin``) whenever the function is applied.

    * Functions capture the environment in effect when they are defined.
      Symbols within the function body can refer to names defined in the
      surrounding lexical context.

    * Function bodies are evaluated in a new environment for each application,
      with the symbols representing the arguments bound to the corresponding
      values in the function application form.

    * Examples:

        ::

            (lambda () 1)

      This defines a constant function (which takes no arguments) whose
      evaluation is always 1.

        ::

            (begin
                (define x 5)
                (lambda () x))

      This defines a constant function whose evaluation is always the value of
      ``x`` in the top-level environment (initially 5).

        ::

            (lambda (a b) (+ a b))

      This defines a binary function (which takes two arguments) whose
      evaluation is the sum of those arguments. This is a simple replacement
      for the ``+`` function itself, but it illustrates the idea that functions
      can include other functions.

* ``define``: A ``define`` form sets the value of a new binding in the current
  environment. This has two forms:

    * ``(define symbol value)``: evaluates the ``value`` subform, and binds the
      result to ``symbol`` in the current environment. Example:

        ::

            (begin
                ; Bind x to a value
                (define x 5)
                ; Expands x in the same environment
                x)

      This program evaluates to ``5``.

    * ``(define (name formals...) body...)``: defines a function and binds it
      to ``name`` in the current environemnt.

      This is expanded to an equivalent ``lambda`` form, within a ``define``
      form binding the resulting procedure to ``name``. For example:

        ::

            (define (f a b) (+ a b))

      is equivalent to

        ::

            (define f
                    (lambda (a b) (+ a b)))

* ``define-macro``: This has the same syntaxes as the ``define`` form, but it
  binds values to a special "macro table" which is used to transform code prior
  to evaluation. Macros are described later in this document.

* ``quote``: A ``quote`` form must have exactly one form in argument position.
  It evaluates to exactly the argument form, without evaluating it. For example:

    ::

        (quote (+ 1 2))

  evaluates to the list ``(+ 1 2)``. Quote forms are the easiest way to obtain
  unevaluated symbols as values, and are an integral part of the Actinide macro
  system.

*******************
Loops and Recursion
*******************

* To loop, a function must recurse. Actinide has no looping primitives other
  than function application.

* Actinide guarantees that functions that recurse in tail position, either
  directly or indirectly, can recurse indefinitely.

* What is tail position?

    * Function bodies: the final form of the function is in tail position with
      respect to the function.

    * ``begin`` forms: the final subform is in tail position with respect to
      the ``begin`` form.

    * ``if`` forms: the ``true`` subform is in tail position with respect to
      the ``if`` form if the ``cond`` subform reduces to a true value. The
      ``false`` subform is in tail position with respect to the ``if`` form if
      the ``cond`` subform reduces to a false value.

    * If a form is in tail position with respect to its containing form, it is
      in tail position with respect to *that* form's containing form, and so
      on, out to the nearest ``lambda`` body or to the top level of the program.

* Example:

    * A simple, non-tail recursive factorial:

        ::

            (define (factorial n)
                    (if (= n 1)
                        1
                        (* n (factorial (- n 1)))))

      The ``factorial`` function *is not* called in tail position with respect
      to the body of the ``factorial`` function: After reducing that function
      application, the reduction of the outer ``factorial`` application still
      needs to apply the ``*`` function to the result.

      Attempting to evaluate ``(factorial 1000)`` fails due to limits on call
      depth: ``maximum recursion depth exceeded while calling a Python object``

        ::

            (define (fact n a)
                    (if (= n 1)
                        a
                        (fact (- n 1) (* n a))))

      The ``fact`` function *is* called in tail position with respect to the
      body of ``fact``. Specifically, it is in tail position with respect to
      the ``if`` form whenever ``n`` is not equal to ``1``, and the ``if`` form
      is in tail position with respect to the body of the ``fact`` function.

      Evaluating ``(fact 1000 1)`` correctly computes the factorial of ``1000``
      on any machine with enough memory to store the result.

******
Macros
******

* Before Actinide evaluates a program, it *expands* a program.

* Expansion replaces macros (defined by ``define-macro``, as above).

* A *macro* is an Actinide procedure, as with ``lambda``, which accepts forms
  as arguments and reduces to a new form.

* Macros can be used to define new syntax.

* Macro expansion is recursive: the result of expanding a macro is expanded
  again, which allows macros to produce macro forms.

* Example: The ``let-one`` macro defines a single local variable, with a known
  value, and evaluates a body form in a temporary environment with that
  variable bound.

    ::

        (define-macro (let-one binding body)
            (begin
                (define name (head binding))
                (define val (head (tail binding)))
                `((lambda (,name) ,body) ,val))))

  To use this macro, apply it as if it were a function:

    ::

        (let-one (x 1) x)

  The macro procedure accepts the forms ``(x 1)`` and ``x``, unevaluated, as
  arguments, and substitutes them into a *quasiquoted* form, which is used as a
  template. The three *unquoted* parts (``,name``, ``,body``, and ``val``) are
  replaced by evaluating the symbols in the context of the macro procedure, and
  expand to the relevant parts of the input forms.

  The returned form is approximately

    ::

      ((lambda (x) x) 1)

  and evaluates as such.

  This program evaluates to 1, but *does not* bind ``x`` in the top-level
  environment.

* Actinide macros are *not hygienic*. A quoted symbol in the macro body will be
  evaluated in the location where the macro is expanded, with full access to
  the environment at that location. Similarly, symbols defined in the macro
  will be fully visible to code running in the environment where the macro is
  expanded.

* Macros often use quote notation to build the returned form. Quote notation is
  ultimately a sequence of ``quote`` forms. However, Actinide supports
  *quasiquote* notation to simplify the creation of nested quoted forms
  containing unquoted parts.

    * A quasiquote form begins with `````. If the form contains no unquoted
      parts, this will quasiquote each subform, terminating by quoting each
      symbol or literal form and constructing a new list with the resulting
      quoted forms. ```(a b)`` expands to ``('a 'b)``.

    * Within a quasiquote form, an *unquote* form prevents the following form
      from being quoted. An unquote form begins with ``,``, followed by a
      single form (often, but not always, a single symbol). ```(a ,b c)``
      expands to ``('a b 'c)``.

    * Within a quasiquote form, an *unquote-splicing* form prevents the
      following form from being quoted. An unquote-splicing form begins with
      ``,@``, followed by a single form, which must evaluate to a list. The
      elements of that list are grafted into the resulting form. Given
      ``(define x (list 1 2))``, the form ```(a ,@x b)`` expands to ``('a 1 2
      'b)``.

* Macros defined inside of a function body are not visible to the top-level
  expander.
