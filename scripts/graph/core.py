import networkx as nx

from data_structure_handlers import ListHandlerStrategy
from data_structure_handlers import DictHandlerStrategy


# --- Core Class
class Core:
    __slots__ = ("_handler",)

    def __init__(self, datastructure_type="lists"):
        handlers = {
            "lists": ListHandlerStrategy(),
            "dicts": DictHandlerStrategy(),
        }

        if datastructure_type not in handlers:
            raise ValueError(
                f"Unsupported data structure type: {datastructure_type}"
            )

        self._handler = handlers[datastructure_type]

    def add_nodes(self, generator_nodes):
        self._handler.add_nodes(generator_nodes)

    def add_edges(self, generator_edges):
        self._handler.add_edges(generator_edges)

    def to_networkx_graph(self, graph_type=nx.DiGraph()):
        return self._handler.to_networkx_graph(graph_type)

    def get_nodes(self):
        return self._handler.get_nodes()

    def get_edges(self):
        return self._handler.get_edges()
