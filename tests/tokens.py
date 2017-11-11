from hypothesis.strategies import just, one_of, characters, text, lists, tuples
from hypothesis.strategies import composite, recursive

# Generators for token families

# Generates the `(` token.
def open_parens():
    return just('(')

# Generates the ')' token.
def close_parens():
    return just(')')

# Generates characters that are legal, unescaped, inside of a string.
def string_bare_characters():
    return characters(blacklist_characters='\\"')

# Generates legal string escape sequences.
def string_escaped_characters():
    return one_of(just('"'), just('\\')).map(lambda c: '\\' + c)

# Generates single-character string representations, including escapes.
def string_characters():
    return one_of(string_bare_characters(), string_escaped_characters())

# Generates arbitrary string bodies (strings, without leading or trailing
# quotes)
def string_body():
    return text(string_characters())

# Generates legal strings.
def strings():
    return tuples(just('"'), string_body(), just('"')).map(lambda t: ''.join(t))

# Generates characters which are legal within a symbol.
def symbol_characters():
    return characters(blacklist_characters=' \t\n();"')

# Generates legal symbols.
def symbols():
    return text(symbol_characters(), min_size=1)

# Generates single whitespace characters.
def whitespace_characters():
    return one_of(just('\n'), just(' '), just('\t'))

# Generates a single token.
def tokens():
    return one_of(symbols(), strings(), open_parens(), close_parens())

# Generates a string which may not be empty, but which does not contain a token.
def nontokens():
    return one_of(whitespace(), comments(), just(''))

# Generates at least one character of whitespace.
def whitespace():
    return text(whitespace_characters(), min_size=1)

# Generates characters which can legally appear inside of a comment (anything
# but a newline).
def comment_characters():
    return characters(blacklist_characters='\n')

# Generates a (possibly-empty) comment, terminated with a trailing newline.
def comments():
    return tuples(just(';'), text(comment_characters()), just('\n')).map(lambda t: ''.join(t))

# Generates sequences which can be inserted between arbitrary pairs of tokens
# without changing their meaning.
def intertokens():
    return one_of(comments(), whitespace())

# Generate a pair such that the second element is a token, and joining the
# elements with an empty string produces a string that tokenizes to the second
# element.
def spaced_tokens():
    def spaced(strategy):
        return tuples(intertokens(), strategy)
    def unspaced(strategy):
        return tuples(one_of(just(''), intertokens()), strategy)
    def spaced_symbols():
        return spaced(symbols())
    def spaced_strings():
        return unspaced(strings())
    def spaced_open_parens():
        return unspaced(open_parens())
    def spaced_close_parens():
        return unspaced(close_parens())

    return one_of(spaced_symbols(), spaced_strings(), spaced_open_parens(), spaced_close_parens())

# Generats a list of pairs as per spaced_token().
def spaced_token_sequences():
    return lists(spaced_tokens())
