from . import builtin, core, stdlib, ports, symbol_table, reader, expander, evaluator, types

# A session with a minimal standard library.
class BaseSession(object):
    def __init__(self):
        self.symbols = symbol_table.SymbolTable()
        self.environment = evaluator.Environment()
        self.core_builtins()
        self.standard_library()

    def read(self, port):
        if types.string_p(port):
            port = ports.string_to_input_port(port)
        return reader.read(port, self.symbols)

    def eval(self, form):
        form = expander.expand(form, self.symbols)
        cps = evaluator.eval(form, self.environment, self.symbols, None)
        return evaluator.run(cps)

    def run(self, port):
        form = self.read(port)
        return self.eval(form)

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

    def bind_module(self, module):
        for name, binding in getattr(module, 'ACTINIDE_BINDINGS', []):
            self.bind(name, binding)
        for fn in getattr(module, 'ACTINIDE_FNS', []):
            self.bind_fn(fn)
        for builtin in getattr(module, 'ACTINIDE_BUILTINS', []):
            self.bind_builtin(builtin)

    def get(self, symb):
        symb = self.symbol(symb)
        return self.environment.find(symb)

    def symbol(self, symb):
        if types.string_p(symb):
            symb = types.symbol(symb, self.symbols)
        return symb

    def core_builtins(self):
        self.bind_module(core)

    def standard_library(self):
        pass

class Session(BaseSession):
    def standard_library(self):
        @self.bind_fn
        def symbol(val):
            return types.symbol(val, self.symbols)
        @self.bind_fn
        def read(port):
            return reader.read(port, self.symbols)
        @self.bind_builtin
        def eval(form):
            return self.eval(form)
        @self.bind_fn
        def expand(form):
            return expander.expand(form, self.symbols)
        self.bind_module(types)
        self.bind_module(stdlib)
        self.bind_module(ports)
