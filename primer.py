import actinide as a
import actinide.types as t
import actinide.expander as x

s = a.Session()

def expand(form):
    return x.expand(form, s.symbols, s.macros)

s.macros[s.symbol('twice')] = lambda f: (t.list(f, f),)
