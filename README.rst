########
Actinide
########

.. image:: https://circleci.com/gh/ojacobson/actinide.svg?style=svg
    :target: https://circleci.com/gh/ojacobson/actinide

.. image:: https://readthedocs.org/projects/pip/badge/
    :target: https://https://actinide.readthedocs.io/


**An embeddable lisp for Python applications.**

I had `an application`_ in which the ability to extend the application from
within, safely, was valuable. None of the languages I reviewed met my criteria:

.. _an application: https://github.com/ojacobson/cadastre/

* `Lua`_ provides `primitives`_ which can be used to interact with the host
  environment, but no facility that guarantees that these tools are
  unavailable. I needed to be able to accept programs from hostile users
  without worrying that they'd overwrite files on the OS.

* `Python itself`_ has the same problem, but more so. Techniques for importing
  arbitrary code even in constrained Python execution environments are well
  known and, as far as I know, unfixable.

* `V8`_ is an attractive option, as it was originally built to evaluate
  Javascript functions in the browser. OS interaction is provided by the
  execution environment, rather than as part of the language's standard
  library. Leaving that out is easy.

  However, the problem space I was working in strongly pushed against using a
  language with no integers and with complex semicolon rules.

.. _Lua: https://www.lua.org
.. _primitives: https://www.lua.org/manual/5.3/manual.html#pdf-os.exit
.. _Python itself: https://python.org/
.. _V8: https://developers.google.com/v8/

So I wrote my own. This is that language.

This is a tiny lisp, along the lines of Peter Norvig's `lispy`_, designed to be
embedded within Python programs. It provides minimal safety features, but the
restricted set of builtins ensures that Actinide programs **probably** cannot
gain access to the outside context of the program. The worst they can do is
waste CPU time, fill up RAM, and drain your battery.

.. _lispy: http://norvig.com/lispy.html

************
Requirements
************

Actinide requires Python 3.6 or later.

Building the documentation requires Sphinx, and should be done in a Python virtual environment:

.. code-block:: bash

    $ python3.6 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements-docs.txt
    $ make html
    $ open _build/html/index.html # or any other command to launch a browser

The documentation is also available online at https://actinide.readthedocs.io.

************
Installation
************

.. code-block:: bash

    $ pip install actinide
    $ pip freeze > requirements.txt

Or, if you prefer, add ``actinide`` to your application's ``Pipfile`` or
``setup.py``.

*****************
Freestanding REPL
*****************

The Actinide interpreter can be started interactively using the
``actinide-repl`` command. In this mode, Actinide forms can be entered
interactively. The REPL will immediately evaluate each top-level form, then
print the result of that evaluation. The environment is persisted from form to
form, to allow interactive definitions.

To exit the REPL, type an end-of-file (Ctrl-D on most OSes, Ctrl-Z on Windows).
