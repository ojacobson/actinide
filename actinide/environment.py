# Raised if a binding cannot be found.
class BindingError(Exception):
    pass

# A lookup table binding symbols to values. This may have a parent environment,
# in which case lookups will look through to the parent environment if they are
# not found in the current environment. This allows nested scopes.
class Environment(dict):
    # Creates an environment, optionally setting initial values and optionally
    # adding a parent to look in for values not found in this environment.
    def __init__(self, bindings=(), parent=None):
        self.parent = parent
        self.update(bindings)

    # Look up a binding in this environment, or in any parent environment.
    # Unlike ``[]``, this will continue into any parent environments, raising an
    # exception if the name cannot be found in any of them.
    #
    # The value from the innermost environment containing the name will be
    # returned.
    def find(self, name):
        if name in self:
            return self[name]
        if self.parent != None:
            return self.parent.find(name)
        raise BindingError(f'Variable {name} not bound')

    # Sets a value in the current environment.
    def define(self, name, value):
        self[name] = value
