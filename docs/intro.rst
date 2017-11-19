########################
Introduction to Actinide
########################

Notes from Slack:

max:
    may i give some unsolicited advice?

owen:
    No, because now I want it so it’s solicited advice instead. What’s up?

max:
    from what you have right now, it reads clearly like it was written by the
    person who wrote the parser for the language

    i would suggest a lighter introduction focusing on: what is this language
    similar to (lisp?), what are its key differences from that other language,
    and a few examples of something in language A versus your language

    more or less, think about what you are looking for when visiting a new
    project (language, library, framework, etc.): what's its purpose, what are
    some simple ways i can do the thing, how is this different from other
    similar projects

    i know it's not especially "technical writing", but IMO that kind of thing
    helps users have a mental framework for reading the rest of the docs

*****************
What is Actinide?
*****************

* A programming language
    * A lisp
    * Heavily inspired by Scheme
* Differences from other languages:
    * Uniform, minimal syntax
    * No operators, only functions
    * The language itself is extensible
    * Functional language
* What's it for?
    * Customizing other programs

**********
Calculator
**********

Concepts introduced:

* Starting the REPL
* What is a REPL?
* Literal forms for numbers
* Built-in arithmetic forms (``+``, ``-``, ``*``, ``/``)
* Simple evaluation ("take the thing on the left, and do it to the rest of the list")

************************
Extending the calculator
************************

Concepts introduced:

* Names, symbols, and environments
* Definition forms (define)
* Flow control forms (if, lambda)
* Recursion

Factorial example.

************
Fixing a bug
************

Concepts introduced:

* *Tail* recursion and why it's special

Redo factorial as a tail-recursive function.

*********************
Thinking functionally
*********************

Concepts introduced:

* Higher-order functions and why they're important
* Reduce

Redo factorial as a fold.

************************
Draw the rest of the owl
************************
