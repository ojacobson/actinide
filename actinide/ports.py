import io

from .builtin import Registry

An = Registry()

# ## PORTS
#
# A port is a handle which characters can either be read from (an "input port")
# or written to (an "output port").
#
# Actinide uses a very limited subset of the full Scheme ports system, and does
# not support the creation of most kinds of port at runtime.

# A port. Under the hood, this wraps a Python file-like object in character
# mode, and guarantees support for peek and other operations needed by the
# Actinide runtime.
class Port(object):
    def __init__(self, file):
        self.file = file
        self.peek_buffer = ''

    # Read up to ``n`` bytes from the port without consuming them.
    def peek(self, n):
        if not self.peek_buffer:
            self.peek_buffer = self.file.read(n)
        return self.peek_buffer

    # Read up to ``n`` bytes from the port, consuming them.
    def read(self, n):
        if self.peek_buffer:
            read_result, self.peek_buffer = self.peek_buffer[:n], self.peek_buffer[n:]
            return read_result
        return self.file.read(n)

    # Read all remaining input, consuming it.
    def read_fully(self):
        return self.peek_buffer + self.file.read()

# Read at least 1 and up to ``n`` characters from a port. This consumes them
# from the port: they are no longer available to future peeks or reads. ``n``
# must be strictly positive.
@An.fn
def read_port(port, n):
    return port.read(n)

# Read all remaining input from a port, consuming it.
@An.fn
def read_port_fully(port):
    return port.read_fully()

# Read at least 1 and up to ``n`` characters from a port, without consuming
# them. They will be available on future peeks and reads. ``n`` must be strictly
# positive.
@An.fn
def peek_port(port, n):
    return port.peek(n)

# Create an input port from a string.
@An.fn
def string_to_input_port(string):
    return Port(io.StringIO(string))
