from . import builtin, core, stdlib, ports, symbol_table, reader, expander, evaluator, types

# A session with a minimal standard library.
class BaseSession(object):
    def __init__(self):
        self.symbols = symbol_table.SymbolTable()
        self.environment = evaluator.Environment()
        self.macros = evaluator.Environment()
        self.core_builtins()
        self.standard_library()

    def read(self, port):
        if types.string_p(port):
            port = ports.string_to_input_port(port)
        return reader.read(port, self.symbols)

    def expand(self, form):
        return expander.expand(form, self.symbols, self.macros)

    def eval(self, form):
        form = self.expand(form)
        cps = evaluator.eval(form, self.symbols, None)
        return evaluator.run(cps, self.environment, self.macros)

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
        symb = self.symbol(name)
        self.bind(symb, fn)
        return symb

    def macro_bind(self, symb, value):
        self.macros[self.symbol(symb)] = value

    def macro_bind_void(self, fn):
        return self.macro_bind_builtin(builtin.wrap_void(fn))

    def macro_bind_fn(self, fn):
        return self.macro_bind_builtin(builtin.wrap_fn(fn))

    def macro_bind_builtin(self, fn):
        name = builtin.lisp_name(fn)
        symb = self.symbol(name)
        self.macro_bind(symb, fn)
        return symb

    def bind_module(self, module):
        registry = module.An
        for name, binding in registry.bindings:
            self.bind(name, binding)
        for name, binding in registry.macros:
            self.macro_bind(name, binding)
        for source in registry.evals:
            self.run(source)

    def get(self, symb):
        symb = self.symbol(symb)
        return self.environment.find(symb)

    def symbol(self, symb):
        if types.string_p(symb):
            symb = types.symbol(symb, self.symbols)
        return symb

    def display(self, form):
        return types.display(form, self.symbols)

    def core_builtins(self):
        @self.bind_fn
        def read(port):
            return reader.read(port, self.symbols)
        @self.bind_builtin
        def eval(form):
            return self.eval(form)
        @self.bind_fn
        def symbol(val):
            return types.symbol(val, self.symbols)
        self.bind_fn(self.expand)
        self.bind_fn(self.display)
        self.bind_module(types)
        self.bind_module(core)

    def standard_library(self):
        pass

class Session(BaseSession):
    def standard_library(self):
        @self.macro_bind_fn
        def let(bindings, *body):
            return stdlib.let(self.symbols, bindings, *body)
        self.bind_module(stdlib)
        self.bind_module(ports)
