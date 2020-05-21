########
Security
########

In the README, I made this strong claim:

    It provides minimal safety features, but the restricted set of builtins
    ensures that Actinide programs probably cannot gain access to the outside
    context of the program. The worst they can do is waste CPU time, fill up
    RAM, and drain your battery.

This document expands on the underlying design choices used to support that
goal.

**I do not promise that Actinide is any more secure than other embeddable
languages**. If you are relying on Actinide to sandbox programs, you do so at
your own risk. If you find a way to escape the sandbox, I very much want to know
about it, and I'll do my best to address it and to communicate this risk to
other users.

**************
Specific Goals
**************

Out of the box, an Actinide ``Session`` must not:

* Read information that is not part of its top-level environment or macro
  table, which was not passed to it as an argument to a method or constructor
  by the enclosing program.

* Write information to any location other than its top-level environment, its
  macro table, or the return value of a method or constructor called by the
  enclosing program.

* Cause system calls that perform IO of any kind.

These goals imply that any externally-visible side effects of Actinide
evaluation are entirely the responsibility of the enclosing program. A "pure"
Actinide environment can only convert electricity into waste heat.

*****
Types
*****

Actinide has a carefully-selected list of built-in types, none of which expose
primitive operations that can gain filesystem access or gain access to
information outside of the Actinide session without without outside help.

Atomic values other than symbols use the least-capable Python representations
possible:

* Python ``int`` objects, used to represent Actinide integers.

* Python ``decimal.Decimal`` objects, used to represent Actinide decimals.

* Python ``str`` objects, used to represent Actinide strings.

* Python ``bool`` objects, used to represent Actinide booleans.

* Python ``list`` objects, used to represent Actinide vectors.

* The Python ``None`` constant, used to represent the empty list.

The remaining built-in types are represented using classes:

* Instances of the ``actinide.types.Symbol`` class, used to represent Actinide
  symbols. This class is a wrapper around a ``str`` and provides only exactly
  the operations needed to act like a sybmol: access to the underlying string,
  equality, hashing, and useful Python ``__str__`` and ``__repr__``
  implementations for debugging.

* Instances of the ``actinide.types.Cons`` class, representing Lisp conses and
  list cells. This class is a ``namedtuple`` with two fields and no additional
  methods. (This implies that conses are immutable, unlike most lisps, but this
  is a semantic consideration and not a security consideration.)

* Instances of the ``actinide.ports.Port`` class, which wraps an arbitrary
  ``file`` object to restrict the operations available. The only built-in
  mechanism for creating a ``Port`` creates one which wraps a string. There are
  no built-in capabilities to open ports that represent files, shared memory
  segments, pipes, processes, sockets, or any other OS resources using only
  built-in functions and types.

* Instances of the ``actinide.types.Procedure`` class, which is considerably
  more complex than the other types. This class handles the mechanics of
  compiling and executing procedures, and allows calling procedure bodies from
  arbitrary Python programs.

  However, ``Procedure`` delegates all of its actual operations back to the
  Actinide runtime, and has effectively the same capabilities as a top-level
  Session.

Finally, built-in functions are represented using Python's own function and
method handle types. The only operations exposed on these are to call them as
Actinide functions, or to extract a string representation including their names.

*********
Functions
*********

Actinide's built-in functions have been selected and implemented for simplicity
of analysis. Actinide avoids exposing complex operations, and _particularly_
avoids exposing any of Python's metaprogramming tools.

Actinide - intentionally - exposes considerably fewer functions than a full
Scheme implementation. Many Scheme functions are inappropriate for Actinide's
use cases, but furthermore, keeping the function set small makes it much easier
to analyze the security properties of the built-in functions.

No built-in function unwraps any type other than as follows:

* ``(string x)`` and ``(display x)``, where ``x`` is a Symbol, unwrap the
  string contained in the symbol object.

* ``(head c)``, ``(tail c)``, and ``(uncons c)``, where ``c`` is a Cons,
  unwraps the head, tail, or both the head and the tail of a Cons.

******
Errors
******

Actinide does not support the full Scheme exception-handling system. Instead,
operations which produce Python exceptions cause the computation to abort at
that point. The exception passes up through the implementation untouched,
allowing the enclosing program to determine how to handle it.
