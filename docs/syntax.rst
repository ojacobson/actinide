######
Syntax
######

.. highlight:: scheme

The most basic unit of Actinide's syntax is the *form*. An Actinide program
consists of a single top-level form, which may include subforms and
sub-subforms within it nested arbitrarily deeply.

********
Comments
********

An Actinide program may contain comments. Comments are removed during parsing
and are not technically forms, but they're included here for completeness. A comment begins with a ``;`` and continues to the next newline character or until the end of the program, whichever comes first.

Examples:

* ``; this is a comment.``

*****
Atoms
*****

The following forms are *atomic* - they do not contain any subforms, and can be
reduced in a single step to a final value.

~~~~~~~~
Integers
~~~~~~~~

An Actinide integer represents a mathematical integer: a precise number with no
fractional part, which may be positive, negative, or zero. Actinide integers do
not have a fixed range - there is no built-in maximum or minimum integer.

The syntax of an integer consists of an optional leading ``-`` sign for
negative integers, followed by any sequence of digits and underscores.
Underscores should be used to separate thousands.

Examples:

* ``10``
* ``-2_049``

.. note::

    Practically, Actinide integers are represented by Python ``int`` objects,
    and share their characteristics. This is not part of their specification,
    but the formal properties of Actinide constracts aren't fully separable
    from the implementation at this time.

~~~~~~~~
Decimals
~~~~~~~~

An Acdinide decimal represents a precise base-ten fractional value with a
finite number of decimal places. Actinide decimals do not have a fixed limit on
range or precision.

The syntax of a decimal consists of an optional leading ``-`` sign for negative
decimal numbers, followed by an optional sequence of digits and underscores for
the integral part, followed by a ``.``, followed by an optional sequence of
digits and underscores for the fractional part, followed by an optional
exponent part consisting of an ``e`` and a sequence of digits and underscores.

A decimal form *must* have a non-empty integral part or a non-empty fractional
part. As with integers, underscores should be used as thousands separators.

Examples:

* ``0.0``
* ``-2_049.501_2``
* ``2e10``

.. note::

    Practically, Actinide decimals are represented by Python
    ``decimal.Decimal`` values in the default decimal context. I haven't fully
    fleshed out the Actinide semantics of decimal operations, so the Python
    semantics leak through. This means that, for example, there is a negative
    zero (which is equal to zero), and that ``1e1`` and ``10`` are different
    (but equal) values.

~~~~~~~
Strings
~~~~~~~

An Actinide string represents a sequence of Unicode characters.

The syntax of a string consists of a leading ``"``, followed by any sequence of
unescaped characters or escaped characters, followed by a trailing ``"``. An
escaped character is either the sequence ``\"`` or the sequence ``\\``; an
unescaped character is any Unicode character other than ``\`` or ``"``. The
enclosing quote marks and escape marks are not part of the string's value, and
are removed during parsing.

Line breaks and non-printing characters can appear within a string.

Examples:

* ``"Hello, world."``
* ``"😡💩🚀"``
* ``"Quoth the raven, \"Four Oh Four.\""``.

.. note::

    As with most other Actinide primitives, strings are implemented directly on
    top of a common Python type: ``str`` itself. The Python representation is
    not part of the language, but does leak through in places.

~~~~~~~~
Booleans
~~~~~~~~

A boolean value represents one of two logical states: true (represented by
exactly ``#t``) and false (``#f``).

~~~~~~~
Symbols
~~~~~~~

Symbols represent variables and special keywords in an Actinide program.

The syntax of a symbol is a sequence of unicode characters other than quotes,
semicolons, tabs, spaces, and newlines, which is not an integer, decimal, or
boolean.

Examples:

* ``x``
* ``if``
* ``+``
* ``my-🚀``

**************
Compound Forms
**************

The following forms consist of both the compound form itself and a sequence of
subforms.

~~~~~
Lists
~~~~~

Lists represent most kinds of Actinide syntax other than atoms.

The syntax of a list consists of an opening ``(``, followed by zero or more
subforms, separated by spaces, tabs, or newlines, followed by a closing ``)``.
The subforms of a list can be any Actinide form, including another list.

Examples:

* ``(foo)``
* ``()``
* ``(1 a #f)``

~~~~~~
Conses
~~~~~~

Conses represent pairs of forms.

The syntax of a dotted pair consists of an opening ``(``, followed by a *head*
form, followed by a ``.``, followed by a *tail* form, followed by a closing
``)``. A dotted pair appearing as the tail of a dotted pair does not need to be
enclosed in parentheses, and can be represented by removing the preceding
``.``, instead.

Examples:

* ``(1 . 2)``
* ``(1 2 . 3)``
* ``((ll . lr) . (rl . rr))``

Conses whose tail form is the empty list are themselves lists. A cons whose
tail form is not a list is an *improper list*.

~~~~~~
Quotes
~~~~~~

A quote form prevents the evaluation of its contained form.

The syntax of a quote form is either a list beginning with the symbol ``quote``
and containing exactly two subforms, or a leading ``'`` followed by a single
form (which is exactly equivalent to ``(quote form)``).

Examples:

* ``'()``, ``(quote ())``
* ``'a``, ``(quote a)``
* ``'(1 . 2)``, ``(quote (1 . 2))``

~~~~~~~~~~~
Quasiquotes
~~~~~~~~~~~

Actinide has a fully-featured :ref:`macro system <macros>`. To support the
macro system, the language includes a system for constructing syntactic forms
programmatically. The following special forms are part of that system:

* ```form``, ``(quasiquote form)``
* ``,form``, ``(unquote form)``
* ``,@form``, ``(unquote-splicing form)``

Full discussion of quasiquoted forms is covered in the section on macros. These
forms cannot be reduced, and will generally raise an error if they're
evaluated, but they're normally eliminated during macro expansion before
evaluation.
