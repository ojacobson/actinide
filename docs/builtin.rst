.. _functions:

##################
Built-In Reference
##################

This document catalogues the built-in functions, built-in values, and macros
provided by Actinide. Host environments may provide additional functions and
macros.

\+
~~

Syntax:

.. code-block:: scheme

    (+ val...)

Arguments:

This function has no fixed arity, and takes zero or more arguments:

* ``val``: any integer or decimal.

Returns:

* The sum of the ``val`` arguments. If all arguments are integers, then the
  result will be an integer. If the arguments include at least one decimal,
  then the result will be a decimal.

\-
~~

Syntax:

.. code-block:: scheme

    (- val)
    (- val val...)

Arguments:

This function has no fixed arity, and takes one or more arguments:

* ``val``: any integer or decimal.

Returns:

With one argument:

* The negation of ``val``.

With multiple arguments:

* The result of subtracting the second and subsequent arguments, in order, from
  the first argument.

\*
~~

Syntax:

.. code-block:: scheme

    (* val val...)

Arguments:

This function has no fixed arity, and takes one or more arguments:

* ``val``: any integer or decimal.

Returns:

* The product of the ``val`` arguments. If all arguments are integers, then the
  result will be an integer; if any argument is a decimal, then the result will
  be a decimal.

/
~

Syntax:

.. code-block:: scheme

    (/ val val...)

Arguments:

This function has no fixed arity, and takes one or more arguments:

* ``val``: any integer or decimal.

Returns:

* The quotient of dividing the first argument by the second and subsequent
  arguments, in order.

If all arguments are integers, the result will be an integer, and the division
will round intermediate results towards negative infinity. If any argument is a
decimal, then all intermediate results will be decimals, with any
unrepresentable intermediate results rounded to the nearest representable value
out to an unspecified number of decimal places.

.. _op-equal:

=
~

Syntax:

.. code-block:: scheme

    (= left right)

Arguments:

* ``left``: any Actinide value.
* ``right``: any Actinide value.

Returns:

* ``#t`` if the arguments ``left`` and ``right`` are *equivalent*, ``#f``
  otherwise.

Any two strings with the same sequence of characters are equivalent.

Any two symbols are equivalent if they have the same string representation and
are interned in the same symbol table.

Any two numbers (integers or decimals, or one of each) are equivalent if they
have the same magnitude.

Any two booleans are equivalent if they have the same logical meaning.

Any two conses are equivalent if their heads are equivalent and their tails are
equivalent.

.. note::

    Note to implementors: this falls through to the python ``==`` operator for
    values it doesn't recognize.

!=
~~

Syntax:

.. code-block:: scheme

    (!= left right)

Arguments:

* ``left``: any Actinide value.
* ``right``: any Actinide value.

Returns:

* ``#t`` if the arguments ``left`` and ``right`` are not equivalent, ``#f``
  otherwise.

Any two strings with the same sequence of characters are equivalent.

Any two symbols are equivalent if they have the same string representation and
are interned in the same symbol table.

Any two numbers (integers or decimals, or one of each) are equivalent if they
have the same magnitude.

Any two booleans are equivalent if they have the same logical meaning.

Any two conses are equivalent if their heads are equivalent and their tails are
equivalent.

<
~

Syntax:

.. code-block:: scheme

    (< left right)

Arguments:

* ``left``: any integer or decimal.
* ``right``: any integer or decimal.

Returns:

* ``#t`` if ``left`` is strictly less than ``right``, ``#f`` otherwise.

<=
~~

Syntax:

.. code-block:: scheme

    (<= left right)

Arguments:

* ``left``: any integer or decimal.
* ``right``: any integer or decimal.

Returns:

* ``#t`` if ``left`` is less than or equal to ``right``, ``#f`` otherwise.

>
~

Syntax:

.. code-block:: scheme

    (> left right)

Arguments:

* ``left``: any integer or decimal.
* ``right``: any integer or decimal.

Returns:

* ``#t`` if ``left`` is strictly greater than ``right``, ``#f`` otherwise.

>=
~~

Syntax:

.. code-block:: scheme

    (>= left right)

Arguments:

* ``left``: any integer or decimal.
* ``right``: any integer or decimal.

Returns:

* ``#t`` if ``left`` is greater than or equal to ``right``, ``#f`` otherwise.

and
~~~

Syntax:

.. code-block:: scheme

    (and val...)

Arguments:

This function has no fixed arity, and takes zero or more arguments:

* ``val``: any Actinide value, but boolean values are preferred.

Returns:

* ``#f`` if any argument is equal to, or coerces to, ``#f``, ``#t`` otherwise.

append
~~~~~~

Syntax:

.. code-block:: scheme

    (append list...)

Arguments:

This function has no fixed arity, and takes zero or more arguments:

* ``list``: any list.

Returns:

* A list composed by appending the arguments to one another, in left-to-right
  order.

Append joins lists, producing a new list whose elements are the elements of the
first argument, followed by the elements of the second, and so on, ending with
the elements of the last argument.

boolean?
~~~~~~~~

Syntax:

.. code-block:: scheme

    (boolean val)

Arguments:

* ``val``: any Actinide value.

Returns:

* ``#t`` if ``val`` is one of the boolean values ``#t`` or ``#f``, ``#f``
  otherwise.

.. _cons:

concat
~~~~~~

Syntax:

.. code-block:: scheme

    (concat string...)

Arguments:

This function has no fixed arity, and takes zero or more arguments:

* ``string``: any string.

Returns:

* The concatenation of the ``string`` arguments, in left-to-right order.

cons
~~~~

Syntax:

.. code-block:: scheme

    (cons head tail)

Arguments:

* ``head``: any Actinide value.
* ``tail``: any Actinide value.

Returns:

* A cons cell whose head and tail are the ``head`` and ``tail`` arguments.

See also:

* :ref:`head`
* :ref:`tail`

cons?
~~~~~

Syntax:

.. code-block:: scheme

    (cons? val)

Arguments:

* ``val``: any Actinide value.

Returns:

* ``#t`` if ``val`` is a cons, including ``nil``; ``#f`` for all other values.

decimal
~~~~~~~

Syntax:

.. code-block:: scheme

    (decimal val)

Arguments:

* ``val``: a string, integer, or decimal value to convert to a decimal.

Returns:

* The decimal value of ``val``, as below.

Converts a value to a decimal.

For strings, this conversion parses the string as if it were an Actinide
decimal literal, and returns the result. If the string cannot be converted in
this manner, this generates an error and aborts computation.

For integers, this conversion returns a decimal value with equal magnitude
whose fractional part is zero.

For decimals, this conversion returns the value unchanged.

decimal?
~~~~~~~~

Syntax:

.. code-block:: scheme

    (decimal? val)

Arguments:

* ``val``: any Actinide value.

Returns:

* ``#t`` if ``val`` is a decimal, ``#f`` for all other values.

.. _display:

display
~~~~~~~

Syntax:

.. code-block:: scheme

    (display val)

Arguments:

* ``val``: any Actinide value.

Returns:

* A string representation of ``val``.

Converts a value into its string representation. For values which are Actinide
forms, the representation can be read back using :ref:`read` to reconstruct
``val``.

See also:

* :ref:`string`

.. note::

    Note to implementors: ``display`` falls back to the Python ``repr()``
    function if it cannot determine the string representation of a value.

eq?
~~~

Syntax:

.. code-block:: scheme

    (eq? left right)

Arguments:

* ``left``: any Actinide value.
* ``right``: any Actinide value.

Returns:

* ``#t`` if ``left`` is identical to ``right``, ``#f`` otherwise.

Identity is somewhat loosely defined. The following cases are guaranteed to be
identical:

* Two expressions that reduce to the same cons.
* Two expressions that reduce to the same vector.
* Two expressions that reduce to the same symbol.
* Two expressions that produce the same boolean value.

Some other cases are also identical as an implementation detail.

.. note::

    Note to implementors: ``eq?`` uses the Python ``is`` operator under the
    hood.

equal?
~~~~~~

See :ref:`= <op-equal>`.

eval
~~~~

Syntax:

.. code-block:: scheme

    (eval form)

Arguments:

* ``form``: an Actinide form (a symbol, literal, or list whose elements are
  forms)

Returns:

* Any type, determined by the result of evaluating ``form``.

Expands and evaluates the Actinide form ``form`` in the top-level environment.

.. _read:

expand
~~~~~~

Syntax:

.. code-block:: scheme

    (expand form)

Arguments:

* ``form``: an Actinide form, which may contain macro calls and other
  unexpanded syntax.

Returns:

* An Actinide form containing no unexpanded macros or unexpanded syntax.

Expands a form, applying macro expansion and converting shorthand forms into
their longhand equivalents.

filter
~~~~~~

Syntax:

.. code-block:: scheme

    (filter fn list)

Arguments:

* ``fn``: a boolean function taking one argument.
* ``list``: any list.

Returns:

* A list, which contains a subset of the entries from ``list``.

The resulting list contains only the values ``v`` from ``list`` where ``(fn
v)`` is true.

.. _head:

head
~~~~

Syntax:

.. code-block:: scheme

    (head cons)

Arguments:

* ``cons``: any cons.

Returns:

* The ``head`` value contained in ``cons``.

See also:

* :ref:`cons`
* :ref:`tail`

integer
~~~~~~~

Syntax:

.. code-block:: scheme

    (integer val)

Arguments:

* ``val``: a string, integer, or decimal value to convert to an integer.

Returns:

* The integer value of ``val``, as below.

Converts a value to an integer.

For strings, this conversion parses the string as if it were an Actinide
integer literal, and returns the result. If the string cannot be converted in
this manner, this generates an error and aborts computation.

For integers, this conversion returns the integer unchanged.

For decimals, this conversion truncates the fractional part of the
decimal (rounding towards zero), and returns the resulting integral part as an
Actinide integer.

integer?
~~~~~~~~

.. code-block:: scheme

    (integer? val)

Arguments:

* ``val``: Any Actinide value.

Returns:

* ``#t`` if the value is an Actinide integer (not including a decimal whose
  fractional part is equal to zero), ``#f`` for all other values.

length
~~~~~~

Syntax:

.. code-block:: scheme

    (length val)

Arguments:

* ``val``: any string or list.

Returns:

* The number of elements in ``val``.

The length of the empty list ``nil`` is zero. The length of any other list is
one greater than the length of its own tail.

The length of a string is the number of characters in that string.

let
~~~

Syntax:

.. code-block:: scheme

    (let (binding...) body...)

A ``binding`` is an expression of the form

.. code-block:: scheme

    (symb form)

Where ``symb`` is a single symbol, and ``form`` is an expression reducing to a
single value.

This macro introduces *local bindings*, which are in effect for the duration of
the ``body`` forms. If the let macro is invoked with an empty list of
``binding`` expressions, it expands to the ``body`` forms (wrapping them in a
``begin`` if necessary), and the result is the result of the last ``body``

form. Otherwise, if the ``let`` macro is invoked with one or more bindings, the
macro creates a local environment with the leftmost binding, then expands
another copy of the ``let`` macro in that environment with the leftmost binding
removed.

Because ``let`` recurses in this manner, binding expressions can refer to any
binding to their left in the same ``let`` expression, but not to bindings to
their right.

Example:

.. code-block:: scheme

    (let ((x 1)         ; x = 1
          (y (+ x 1)))  ; y = 2
         (+ x y))       ; result = x + y = 3

This program reduces to ``3``, without creating bindings for ``x`` and ``y``
that live beyond the evaluation of the ``let`` form.

list
~~~~

Syntax:

.. code-block:: scheme

    (list elem...)

Arguments:

This function has no fixed arity, and takes zero or more arguments:

* ``elem``: any Actinide value

Returns:

* A list of the ``elem`` values, in left-to-right order.

A *list* is either nil (the result of ``(list)`` without arguments), or a cons
whose head is the value at that position and whose tail is a list. This
function constructs a list from its arguments, with the leftmost argument in
the first position of the resulting list and the rightmist argument in the last.

See also:

* :ref:`cons`

list?
~~~~~

Syntax:

.. code-block:: scheme

    (list? val)

Arguments:

* ``val``: any Actinide value

Returns:

* ``#t`` if ``val`` is a list, ``#f`` for all other values.

list-to-vector
~~~~~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (list-to-vector list)

Arguments:

* ``list``: any list.

Returns:

* A vector containing the same elements as ``list``, in the same order.

map
~~~

Syntax:

.. code-block:: map

    (map fn list)

Arguments:

* ``fn``: any procedure accepting one value and returning one value.
* ``list``: any list.

Returns:

* A list of results.

Applies ``fn`` to each element of ``list``, returning a list of the resulting
values in the same order.

.. _nil:

nil
~~~

Syntax:

.. code-block:: scheme

    nil

Returns:

* The empty list.

nil?
~~~~

Syntax:

.. code-block:: scheme

    (nil? val)

Arguments:

* ``val``: any value.

Returns:

* A boolean. ``#t`` if ``val`` is equal to :ref:`nil`, otherwise ``#f``.

Checks if a value is nil.

not
~~~

Syntax:

.. code-block:: scheme

    (not val)

Arguments:

* ``val``: any Actinide value, although a boolean is preferred.

Returns:

* The boolean negation of ``val``: ``#t`` if the argument ``val`` is ``#f``, or
  ``#f`` if ``val`` is ``#t``.

or
~~

Syntax:

.. code-block:: scheme

    (or val...)

Arguments:

This function has no fixed arity, and takes zero or more arguments:

* ``val``: any Actinide value, although boolean values are preferred.

Returns:

* ``#t`` if any argument is ``#t`` or coerces to true, ``#f`` otherwise.

peek-port
~~~~~~~~~

Syntax:

.. code-block:: scheme

    (peek-port port len)

Arguments:

* ``port``: an input port.
* ``len``: an integer length.

Returns:

* Up to ``len`` characters from ``port``, without consuming them.

This will peek ahead into the port, reading into an internal buffer if
necessary, and return at least 1 and up to ``len`` characters that will be
available to ``read-port``. If the stream is fully consumed, this returns the
empty string.

procedure?
~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (procedure? val)

Arguments:

* ``val``: any Actinide value.

Returns:

* ``#t`` if ``val`` is a procedure (either produced by a ``lambda`` form or a
  built-in procedure provided by the host environment or the implementation),
  ``#f`` for all other values.

read
~~~~

Syntax:

.. code-block:: scheme

    (read port)

Arguments:

* ``port``: an input port. By default, input ports can be created from strings
  using :ref:`string-to-input-port`; the host environment may provide other
  facilities.

Returns:

* A form, or the special uninterned symbol ``#<end-of-file>``.

Reads one form from the given input port ``port`` and returns it. If the reader
encounters the end of input, this returns a generated symbol indicating end of
input.

read-port
~~~~~~~~~

Syntax:

.. code-block:: scheme

    (read-port port len)

Arguments:

* ``port``: an input port.
* ``len``: an integer length.

Returns:

* Up to ``len`` characters read from ``port``.

This consumes the characters returned - they will not be returned in future
calls to ``peek-port`` or ``read-port`` on the same port. If the port is fully
consumed, this will return the empty string.

read-port-fully
~~~~~~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (read-port-fully port)

Arguments:

* ``port``: an input port.

Returns:

* All remaining characters in ``port``.

This consumes the characters returned - they will not be returned in future
calls to ``peek-port`` or ``read-port`` on the same port. If the port is fully
consumed, this will return the empty string.

reduce
~~~~~~

Syntax:

.. code-block:: scheme

    (reduce fn list)

Arguments:

* ``fn``: any procedure taking two arguments and returning one value.
* ``list``: any non-empty list.

Returns:

* The result of reducing the list through ``fn``, in left-to-right order.

This passes the first two elements of ``list`` to ``fn``, then passes the
result and the third element of ``list`` to ``fn``, and so on, until the list
is exhausted, and returns the result. As a special case, if ``list`` has a
single element, this returns it as-is.

.. _string:

string
~~~~~~

Syntax:

.. code-block:: scheme

    (string val)

Arguments:

* ``val``: any Actinide value.

Returns:

* A human-readable string representation of that value.

Converts a value to a human-readable string.

For strings, this returns the value unchanged.

For integers and decimals, this returns a string representation of the number.

See also:

* :ref:`display`

.. note::

    Note to implementors: this falls back to the Python ``str()`` function if
    it cannot determine a string representation of the value.

string?
~~~~~~~

Syntax:

.. code-block:: scheme

    (string? val)

Arguments:

* ``val``: any Actinide value.

Returns:

* ``#t`` if ``val`` is a string, ``#f`` for all other values.

.. _string-to-input-port:

string-to-input-port
~~~~~~~~~~~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (string-to-input-port str)

Arguments:

* ``str``: any string.

Returns:

* A fresh input port, whose characters will be drawn from ``str`` in order.

This is the only built-in procedure Actinide provides for constructing input
ports from within Actinide programs.

symbol
~~~~~~

Syntax:

.. code-block:: scheme

    (symbol string)

Arguments:

* ``string``: a string.

Returns:

* An interned symbol.

Converts a string ``string`` into an equivalent symbol, interning it if necessary. The following equivalences hold for all strings ``S``:

.. code-block:: scheme

    (= (symbol S) (symbol S))
    (eq? (symbol S) (symbol S))

.. note::

    Note to host program implementors: Symbols are interned on a per-session
    basis. The above equivalences do not hold for symbols obtained from
    different sessions.

symbol?
~~~~~~~

Syntax:

.. code-block:: scheme

    (symbol? val)

Arguments:

* ``val``: any Actinide value.

Returns:

* ``#t`` if ``val`` is a symbol, ``#f`` for all other values.

.. _tail:

tail
~~~~

Syntax:

.. code-block:: scheme

    (tail cons)

Arguments:

* ``cons``: any cons.

Returns:

* The ``tail`` value contained in ``cons``.

See also:

* :ref:`cons`
* :ref:`head`

uncons
~~~~~~

Syntax:

.. code-block:: scheme

    (uncons cons)

Arguments:

* ``cons``: any cons.

Returns:

This function returns two values:

* The ``head`` contained in the cons, and
* The ``tail`` contained in the cons.

vector
~~~~~~

Syntax:

.. code-block:: scheme

    (vector elem...)

Arguments:

This function has no fixed arity, and takes zero or more arguments:

* ``elem``: any Actinide value.

Returns:

* A vector containing the given elements, in left-to-right order.

A *vector* is an ordered container guaranteeing amortized constant-time indexed
access to its elements (compared to a list's amortized linear time access to a
specific index).

vector?
~~~~~~~

Syntax:

.. code-block:: scheme

    (vector? val)

Arguments:

* ``val``: any Actinide value.

Returns:

* ``#t`` if ``val`` is a vector, ``#f`` for all other values.

vector-add
~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (vector-add vec elem...)

Arguments:

This argument has no fixed arity, and takes one or more arguments:

* ``vec``: any vector.
* ``elem``: any Actinide value.

Returns:

* ``vec``.

This function modifies ``vec`` as a side effect, appending each ``elem`` to the
end of the vector, in left-to-right order (so that the last argument is the
vector's new last element).

vector-get
~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (vector-get vec idx)

Arguments:

* ``vec``: any vector.
* ``idx``: an integer index.

Returns:

* The element of ``vec`` at index ``idx``.

The index ``idx`` must be no less than zero, and less than the vector's
``vector-length``. Values outside of this range will raise an error and abort
computation.

vector-length
~~~~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (vector-length vec)

Arguments:

* ``vec``: any vector.

Returns:

* The number of elements in ``vec``.

vector-set
~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (vector-set vec idx elem)

Arguments:

* ``vec``: any vector.
* ``idx``: an integer intex.
* ``elem``: any Actinide value.

Returns:

* ``vec``.

This function modifies ``vec`` as a side effect. The element at index ``idx``
is replaced with ``elem``. As with ``vector-get``, the index ``idx`` must be no
less than zero and less than the vector's ``vector-length``.

vector-to-list
~~~~~~~~~~~~~~

Syntax:

.. code-block:: scheme

    (vector-to-list vec)

Arguments:

* ``vec``: any vector.

Returns:

* A list containing the same elements as ``vec``, in the same order.


