from csv import reader as csv_reader

import networkx as nx

from core import Core
from data_structure_handlers import ListHandlerStrategy
from data_structure_handlers import DictHandlerStrategy


def load_csv_generator(file_path, header=True):
    with open(file_path, "r") as file:
        reader = csv_reader(file)
        if header:
            next(reader)
        for row in reader:
            yield tuple(row)


# ---------------- Usability ----------- class

# Read data from CSV as generator
generator_nodes = load_csv_generator(
    "../../data_examples/dataset_dummy2_nodes.csv"
)
generator_edges = load_csv_generator(
    "../../data_examples/dataset_dummy2_edges.csv"
)

# Create the object Core containing our internal representation
my_core = Core(datastructure_type="dicts")

# Add nodes
my_core.add_nodes(generator_nodes=generator_nodes)

# Add edges
my_core.add_edges(generator_edges=generator_edges)


# Show me the content of our core
print("Nodes: ")

if isinstance(my_core.get_nodes(), list):
    for node in my_core.get_nodes():
        print(node)
if isinstance(my_core.get_nodes(), dict):
    for node in my_core.get_nodes().keys():
        print(node)

print(my_core.get_nodes())

# G = my_core.to_networkx_graph(graph_type=nx.DiGraph())
# print("#-------- Number of nodes in the graph")
# print(G.number_of_nodes())
# print(G.nodes(data=True))
