import actinide

def test_known_expansion():
    s = actinide.Session()
    s.run('''
        (begin
            (define-macro (let-one binding body)
                (begin
                    (define name (head binding))
                    (define val (head (tail binding)))
                    `((lambda (,name) ,body) ,val))))
    ''')
    program = s.read('(let-one (x 1) x)')
    assert s.symbol('x') not in s.environment
    assert (1,) == s.eval(program)

def test_quasiquote_expansion():
    s = actinide.Session()

    program = s.read('`(a ,b c)`')
    expansion = s.expand(program)
    assert s.read("(cons 'a (cons b (cons 'c ())))") == expansion

def test_nested_qq_expansion():
    s = actinide.Session()

    program = s.read('`((,a))`')
    expansion = s.expand(program)
    assert s.read("(cons (cons a ()) ())") == expansion

def test_shorter_qq_expansion():
    s = actinide.Session()

    program = s.read('`(,a b)`')
    expansion = s.expand(program)
    assert s.read("(cons a (cons 'b ()))") == expansion
