from abc import abstractmethod
from typing import Union
from cypherweb.core.graph import Graph


class Node:
    """Base for pipeline building blocks."""

    @abstractmethod
    def process(self, graph: Graph) -> None:
        """Apply a transformation on ``graph``."""

    @abstractmethod
    def run(self, payload: dict, params=None) -> None:
        pass

    # def update_passing_input(
    #     self, passing_input: dict, node_key: str, output: dict
    # ) -> None:
    #     passing_input[node_key] = output

    def __call__(self, inputs: Union[dict, Graph], params: dict = None) -> None:
        if isinstance(inputs, Graph):
            self.process(inputs)
        else:
            output = self.run(inputs, params)
            return output
