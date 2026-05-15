from typing import Iterator
import contextlib

class Codebuilder(object):
    def __init__(self):
        self.blocks = []
        self.code = []

    def get_code(self):
        # type: () -> str
        """Returns the generated code as a single string with proper indentation."""
        assert not self.blocks
        return "\n".join(["    " * depth + line for depth, line in self.code])

    def make_parser(self):
        # type: () -> type
        """Compiles the generated code and returns the Parser class."""
        m = {'Status': Status,
             'Nonterminal': Nonterminal,
             'Symbol': Symbol,}
        exec(py.code.Source(self.get_code()).compile(), m)
        return m['Parser']

    def emit(self, line):
        # type: (str) -> None
        """Appends a line of code to the builder, handling multi-line strings."""
        for line in line.split("\n"):
            if line:
                self.code.append((len(self.blocks),  line))

    def emit_initcode(self, line):
        # type: (str) -> None
        """Appends a line to the init code block."""
        for line in line.split("\n"):
            self.initcode.append(line)

    def start_block(self, blockstarter):
        # type: (str) -> None
        """Emits a block starter line and pushes it onto the block stack."""
        assert blockstarter.endswith(":")
        self.emit(blockstarter)
        self.blocks.append(blockstarter)

    @contextlib.contextmanager
    def block(self, blockstarter):
        # type: (str) -> Iterator[None]
        """Context manager that starts a block and automatically ends it after the with body."""
        self.start_block(blockstarter)
        yield None
        self.end_block(blockstarter)

    def end_block(self, starterpart=""):
        # type: (str) -> None
        """Closes the most recent block, asserting the given starterpart matches."""
        block = self.blocks.pop()
        assert starterpart in block, "ended wrong block %s with %s" % (
            block, starterpart)

    def store_code_away(self):
        # type: () -> tuple[list, list]
        """Saves the current block and state, clears it, and returns the saved values."""
        result = self.blocks, self.code
        self.code = []
        self.blocks = []
        return result
    def restore_code(self, (blocks, code)):
        # type: (tuple[list, list]) -> tuple[list, list]
        """Restores saved block and state, returning the previous values."""

        result = self.blocks, self.code
        self.code = code
        self.blocks = blocks
        return result
    def add_code(self, (blocks, code)):
        # type: (tuple[list, list]) -> None
        """Appends saved block and state to the current builder."""
        self.code += [(depth + len(self.blocks), line) for depth, line in code]
        self.blocks += blocks
 
