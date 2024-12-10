import ast
import cProfile
import csv
import os
import pstats

import networkx as nx
from pympler import asizeof
from tabulate import tabulate

FILE_PATH_DATASETS = "data_examples"


# ----------------  HELPER FUNCTIONS
def profile_objects_pympler(**kwargs):
    sizes_mebibytes = []
    for object in kwargs.keys():
        size_summary = asizeof.asized(kwargs[object], detail=0).format()

        total_size_mebibytes = float(size_summary.split(" ")[-2].split("=")[1])
        total_size_mebibytes /= 1024**2

        flat_size_mebibytes = float(size_summary.split(" ")[-1].split("=")[1])
        flat_size_mebibytes /= 1024**2

        sizes_mebibytes.append(
            [
                object,
                type(kwargs[object]),
                total_size_mebibytes,
                flat_size_mebibytes,
            ]
        )

    return sizes_mebibytes


def print_pympler_results(results):
    print(
        tabulate(
            results,
            headers=[
                "Variable",
                "object",
                "Total Size [MiB]",
                "Flat Size [MiB]",
            ],
        )
    )


def pymper_profiler(**kwargs):
    print("\nProfiling objects with Pympler...")
    results_pympler = profile_objects_pympler(**kwargs)
    print_pympler_results(results_pympler)


# ----------------  FUNCTIONS PIPELINE
def load_csv_generator(file_path, header=True):
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        if header:
            next(reader)
        for row in reader:
            yield tuple(row)


def create_lists(file_path_nodes, file_path_edges, header_nodes=True, header_edges=True):

    nodes_ds = load_csv_generator(file_path_nodes, header=header_nodes)
    edges_ds = load_csv_generator(file_path_edges, header=header_edges)

    list_nodes = [item for item in nodes_ds]
    list_edges = [item for item in edges_ds]

    return list_nodes, list_edges


def to_networkx_nodes_format(nodes_iterable, mapping_properties=True):
    for node_id, node_label, properties in nodes_iterable:
        # Original format
        #  (node id, node label, properties)

        # Desired format
        #  (node id, properties as dict)

        properties = ast.literal_eval(properties)

        if mapping_properties:
            properties["node_label"] = node_label

        yield (node_id, properties)


def to_networkx_edges_format(edges_iterable, mapping_properties=True):
    for edge_tuple in edges_iterable:
        edge_id, source_id, target_id, edge_label, properties = edge_tuple

        # Original format
        #  (edge id, source (edge id), target (edge id), label, properties)

        # Desired format
        #  (source (edge id), target (edge id), properties as dict)

        properties = ast.literal_eval(properties)

        if mapping_properties:
            properties["edge_id"] = edge_id
            properties["edge_label"] = edge_label

        yield (
            source_id,
            target_id,
            properties,
        )


def networkx_graph_from_lists(nodes_iterable, edges_iterable, graph_type=nx.DiGraph()):
    # Create an empty graph
    networkx_graph = graph_type

    # Populate the graph with edges and their properties
    networkx_graph.add_edges_from(edges_iterable)

    # Populate the graph with nodes and their properties
    networkx_graph.add_nodes_from(nodes_iterable)

    return networkx_graph


# ----------------  MAIN FUNCTION
def main():

    filename_nodes = "dataset_30000_nodes_proteins.csv"
    filename_edges = "dataset_30000_edges_interactions.csv"

    file_path_nodes = os.path.join(FILE_PATH_DATASETS, filename_nodes)
    file_path_edges = os.path.join(FILE_PATH_DATASETS, filename_edges)

    print(os.getcwd())

    # ------------------  TIME STATS  -------------------------
    print("======   Time profile")
    # Create a cProfiler
    profiler = cProfile.Profile()
    profiler.enable()

    ds_list_nodes, ds_list_edges = create_lists(
        file_path_nodes, file_path_edges, header_nodes=True, header_edges=True
    )

    profiler.disable()

    # Print cProfile statistics
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(30)

    # ------------------  MEMORY STATS  -------------------------
    print("======   Memory profile\n")
    print("Example nodes:\n\t{}".format(ds_list_nodes[0:1]))
    print("Example edges:\n\t{}".format(ds_list_edges[0:1]))

    # IMPORTANT: Comment the following line is profile with Memray
    # pymper_profiler(nodes=ds_list_nodes, edges=ds_list_edges, integer=10)


# ----------------  Entry point script
if __name__ == "__main__":
    main()
