from . import builtin, ports, symbol_table, reader, expander, evaluator, types

class Session(object):
    def __init__(self):
        self.symbols = symbol_table.SymbolTable()
        self.environment = evaluator.Environment()

    def read(self, port):
        if types.string_p(port):
            port = ports.string_to_input_port(port)
        form = reader.read(port, self.symbols)
        return expander.expand(form, self.symbols)

    def eval(self, form):
        cps = evaluator.eval(form, self.environment, self.symbols, None)
        return evaluator.run(cps)

    def bind(self, symb, value):
        self.environment[self.symbol(symb)] = value

    def bind_void(self, fn):
        return self.bind_builtin(builtin.wrap_void(fn))

    def bind_fn(self, fn):
        return self.bind_builtin(builtin.wrap_fn(fn))

    def bind_builtin(self, fn):
        name = builtin.lisp_name(fn)
        if name is None:
            raise ValueError("Anonymous functions must be bound using `bind`")
        symb = self.symbol(name)
        self.bind(symb, fn)
        return symb

    def get(self, symb):
        symb = self.symbol(symb)
        return self.environment.find(symb)

    def symbol(self, symb):
        if types.string_p(symb):
            symb = types.symbol(symb, self.symbols)
        return symb
