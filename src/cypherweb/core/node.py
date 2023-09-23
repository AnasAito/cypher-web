from abc import abstractmethod
from typing import Union
from cypherweb.core.graph import Graph


class Node:
    """Base for pipeline building blocks."""

    @abstractmethod
    def process(self, graph: Graph) -> None:
        """Apply a transformation on ``graph``."""

    @abstractmethod
    def run(self, payload: Union[dict, str], params=None) -> None:
        pass

    def __call__(self, inputs: Union[dict, Graph, str], params: dict = None):
        if isinstance(inputs, Graph):
            # we diff beteween process and run a process is used to run sub-pipelines as nodes
            # to be normalized in the future ! (I dont like it)
            self.process(inputs)
        else:
            output = self.run(inputs, params)
            return output
