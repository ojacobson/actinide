import actinide
import actinide.types as t
import actinide.builtin as b
import actinide.evaluator as e

session = actinide.Session()
program = session.read("""
(begin
    1
    1.0
    "Hello"
    (define a
        (lambda (b) (values 1 2.2 "three" a b)))
    (define pp
        (lambda () (pp)))
    (print (a "foo"))
    (print (eval (list (symbol "a") "bar")))
    (print 0 (values 1 2 3) 4 5)
    (pp))
""")

def begin(*args):
    if args:
        return args[-1]
    return None

def values(*args):
    return args

session.bind_builtin(values)
session.bind_void(print)
session.bind_fn(begin)
session.bind_fn(t.list)
session.bind_fn(session.symbol)
session.bind_builtin(session.eval)

session.eval(program)
