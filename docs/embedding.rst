##################
Embedding Actinide
##################

Actinide is designed to be embedded into larger Python programs. It's possible
to call into Actinide, either by providing code to be evaluated, or by
obtaining builtin functions and procedures from Actinide and invoking them.

The ``Session`` class is the basic building block of an Actinide integration.
Creating a session creates a number of resources associated with Actinide
evaluation: a symbol table for interning symbols, and an initial top-level
environment to evaluate code in, pre-populated with the Actinide standard
library.

Executing Actinide programs in a session consists of two steps: reading the
program in from a string or an input port, and evaluating the resulting forms.
The following example illustrates a simple infinite loop:

.. code-block:: python

    import actinide

    session = actinide.Session()
    program = session.read('''
        (begin
            ; define the factorial function
            (define (factorial n)
                (fact n 1))

            ; define a tail-recursive factorial function
            (define (fact n a)
                (if (= n 1)
                    a
                    (fact (- n 1) (* n a))))

            ; call them both
            (factorial 100))
    ''')

    # Compute the factorial of 100
    result = session.eval(program)

As a shorthand for this common sequence of operations, the Session exposes a
``run`` method:

.. code-block:: python

    print(*session.run('(factorial 5)')) # prints "120"

Callers can inject variables, including new builtin functions, into the initial
environment using the ``bind``, ``bind_void``, ``bind_fn``, and
``bind_builtin`` methods of the session.

To bind a simple value, or to manually bind a wrapped builtin, call
``session.bind``:

.. code-block:: python

    session.bind('var', 5)
    print(*session.run('var')) # prints "5"

To bind a function whose return value should be ignored, call ``bind_void``.
This will automatically determine the name to bind the function to:

.. code-block:: python

    session.bind_void(print)
    session.run('(print "Hello, world!")') # prints "Hello, world!" using Python's print fn

To bind a function returning one value (most functions), call ``bind_fn``. This
will automatically determine the name to bind to:

.. code-block:: python

    def example():
        return 5

    session.bind_fn(example)
    print(*session.run('(example)')) # prints "5"

To bind a function returning a tuple of results, call ``bind_builtin``. This
will automatically determine the name to bind to:

.. code-block:: python

    def pair():
        return 1, 2

    session.bind_builtin(pair)
    print(*session.run('(pair)')) # prints "1 2"

Actinide functions can return zero, one, or multiple values. As a result, the
``result`` returned by ``session.eval`` is a tuple, with one value per result.

Actinide can bind Python functions, as well as bound and unbound methods, and
nearly any other kind of callable. Under the hood, Actinide uses a thin adapter
layer to map Python return values to Actinide value lists. The ``bind_void``
helper ultimately calls that module's ``wrap_void`` to wrap the function, and
``bind_fn`` calls ``wrap_fn``. (Tuple-returning functions do not need to be
wrapped.) If you prefer to manually bind functions using ``bind``, they must be
wrapped appropriately. An equivalent set of methods, ``macro_bind``,
``macro_bind_void``, ``macro_bind_fn``, and ``macro_bind_builtin`` bind values
to entries in the top-level macro table, instead of the top-level environment,
and allow extension of the language's syntax.

Finally, Actinide can bind specially-crafted Python modules. If a module
contains a top-level symbol named ``An`` (for the informal chemical symbol for
the actinide series), it can be passed to the session's ``bind_module`` method.
The symbol must be bound to an instance of the ``Registry`` class from the
``actinide.builtin`` module:

.. code-block:: python

    from actinide.builtin import Registry
    An = Registry()

    five = An.bind('five', 5)

    @An.void
    def python_print(*args):
        print(*args)

    @An.fn
    def bitwise_and(a, b):
        return a & b

    @An.builtin
    def two_values():
        return 1, "Two"

    An.eval('''
        (begin
            (define (three-values) (values 1 2 3)))
    ''')

    # @An.macro_bind, @An.macro_void, @An.macro_fn, and @An.macro_builtin follow
    # the same pattern.

Going the other direction, values can be extracted from bindings in the session
using the ``get`` method:

.. code-block:: python

    session.run('(define x 8)')
    print(session.get('x')) # prints "8"

If the extracted value is a built-in function or an Actinide procedure, it can
be invoked like a Python function. However, much like ``eval`` and ``run``,
Actinide functions returne a tuple of results rather than a single value:

.. code-block:: python

    session.run('''
        (begin
            ; Set a variable
            (define x 5)

            ; Define a function that reads the variable
            (define (get-x) x))
    ''')

    get_x = session.get('get-x')
    print(*get_x()) # prints "5"

This two-way binding mechanism makes it straightforward to define interfaces
between Actinide and the target domain.

.. todo::

    Document the full public API.
