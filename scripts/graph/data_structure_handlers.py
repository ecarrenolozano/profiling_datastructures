# --- Base Abstract Class for Handlers
from abc import ABC, abstractmethod
from collections import defaultdict

import networkx as nx

from utils import edge_to_format_three_fields
from utils import node_to_format_two_fields


class DataStructureHandlerStrategy(ABC):
    @abstractmethod
    def get_nodes(self):
        pass

    @abstractmethod
    def get_edges(self):
        pass

    @abstractmethod
    def add_nodes(self, generator_nodes):
        pass

    @abstractmethod
    def add_edges(self, generator_edges):
        pass

    @abstractmethod
    def to_networkx_graph(self, graph_type):
        pass


# --- List Handler
class ListHandlerStrategy(DataStructureHandlerStrategy):
    def __init__(self):
        self.nodes = list()
        self.edges = list()

    def add_nodes(self, generator_nodes):
        self.nodes.extend(generator_nodes)

    def add_edges(self, generator_edges):
        self.edges.extend(generator_edges)

    def to_networkx_graph(self, graph_type=nx.DiGraph()):
        _transformation_nodes = node_to_format_two_fields(self.nodes)
        _transformation_edges = edge_to_format_three_fields(self.edges)

        _networkx_graph = graph_type
        _networkx_graph.add_edges_from(_transformation_edges)
        _networkx_graph.add_nodes_from(_transformation_nodes)

        return _networkx_graph

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges


# --- Dict Handler
class DictHandlerStrategy(DataStructureHandlerStrategy):
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_nodes(self, generator_nodes):
        _transformation = node_to_format_two_fields(generator_nodes)
        self.nodes.update(
            {node_id: properties for node_id, properties in _transformation}
        )

    def add_edges(self, generator_edges):
        _transformation = edge_to_format_three_fields(generator_edges)
        _adjacency_map = defaultdict(dict)

        for source_id, target_id, properties in _transformation:
            _adjacency_map[source_id][target_id] = properties

        self.edges.update(_adjacency_map)

    def to_networkx_graph(self, graph_type=nx.DiGraph()):
        _networkx_graph = nx.from_dict_of_dicts(
            self.edges, create_using=graph_type
        )
        _networkx_graph.add_nodes_from(self.nodes.items())
        return _networkx_graph

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges
