import os
import platform
import pstats
from ast import literal_eval
from collections import defaultdict
from cProfile import Profile
from csv import reader as csv_reader
from itertools import islice
from json import dumps

import networkx as nx
import pandas as pd
from memray import Tracker as memray_tracker
from pympler import asizeof
from tabulate import tabulate


# =====================================================================
# ==================       Additional Functions      ==================
# =====================================================================
def clear_console():
    if platform.system() == "Windows":
        os.system("cls")  # Windows
    else:
        os.system("clear")  # Unix/Linux/MacOS


def print_metadata(file_path_nodes, file_path_edges):
    print("--------------------------------------------------------------------")
    print("------------------       Profiling Pipeline       ------------------")
    print("--------------------------------------------------------------------")
    print("Metadata")
    print("\tScript's name:\t{}".format(os.path.basename(__file__)))
    print(
        "\tData for nodes: {}\n\tData for edges: {}".format(
            file_path_nodes, file_path_edges
        )
    )


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


def pympler_profiler(**kwargs):
    print("\nProfiling objects with Pympler...\n")
    results_pympler = profile_objects_pympler(**kwargs)
    print_pympler_results(results_pympler)


def example_info_networkx_graph(graph):
    limit = 2
    print("\nExample NetworkX nodes:")
    for index, node in enumerate(graph.nodes(data=True)):
        if index == limit:
            break
        print(node)

    print("\nExample NetworkX edges:")
    for index, edge in enumerate(graph.edges(data=True)):
        if index == limit:
            break
        print(edge)

    print("Graph size: {}".format(graph.size()))


# =====================================================================
# ==================       Functions Pipeline        ==================
# =====================================================================
def load_csv_generator(file_path, header=True):
    with open(file_path, "r") as file:
        reader = csv_reader(file)
        if header:
            next(reader)
        for row in reader:
            yield tuple(row)


def to_networkx_nodes_format(nodes_iterable, mapping_properties=True):
    for node_id, node_label, properties in nodes_iterable:
        # Original format
        #  (node id, node label, properties)

        # Desired format
        #  (node id, properties as dict)

        properties = literal_eval(properties)

        if mapping_properties:
            properties["node_label"] = node_label

        yield (node_id, properties)


def to_networkx_edges_format(edges_iterable, mapping_properties=True):
    for edge_id, source_id, target_id, edge_label, properties in edges_iterable:
        # Original format
        #  (edge id, source (edge id), target (edge id), label, properties)

        # Desired format
        #  (source (edge id), target (edge id), properties as dict)

        properties = literal_eval(properties)

        if mapping_properties:
            properties["edge_id"] = edge_id
            properties["edge_label"] = edge_label

        yield (
            source_id,
            target_id,
            properties,
        )


def generate_nodes_dict(generator_nodes):
    return {node: properties for (node, properties) in generator_nodes}


def create_adjacency_map(generator_edges):

    adjacency_map = defaultdict(dict)

    for source_id, target_id, properties in generator_edges:
        adjacency_map[source_id][target_id] = properties

    return adjacency_map


def create_dictionaries(file_path_nodes, file_path_edges):
    nodes_ds = load_csv_generator(file_path_nodes, header=True)
    nodes_ds = to_networkx_nodes_format(nodes_ds)
    nodes_ds = generate_nodes_dict(nodes_ds)

    edges_ds = load_csv_generator(file_path_edges, header=True)
    edges_ds = to_networkx_edges_format(edges_ds)
    edges_ds = create_adjacency_map(edges_ds)

    return nodes_ds, edges_ds


def networkx_graph_from_dicts(nodes_dict, adjacency_map, graph_type=nx.DiGraph()):
    # Create and populate graph using an adjacency map
    networkx_graph = nx.from_dict_of_dicts(adjacency_map, create_using=graph_type)

    # Populate nodes with properties
    networkx_graph.add_nodes_from(nodes_dict.items())

    return networkx_graph


def pipeline(file_path_nodes, file_path_edges):
    # Task 1. Create data structures for the internal representation
    nodes_dict, edges_adjacency_map = create_dictionaries(
        file_path_nodes, file_path_edges
    )

    # Task 2. Create a NetworkX graph based on the internal representation
    # Dictionaries to change the name of columns to maintain compatibility with Networkx
    graph = networkx_graph_from_dicts(
        nodes_dict=nodes_dict,
        adjacency_map=edges_adjacency_map,
        graph_type=nx.DiGraph(),
    )

    return nodes_dict, edges_adjacency_map, graph


# =====================================================================
# ==================            MAIN Function        ==================
# =====================================================================

if __name__ == "__main__":

    # Clear the console in Windows/Unix/Linux
    clear_console()

    # MODIFY THIS: Path to the datasets
    FILE_PATH_DATASETS = "../data_examples"
    FILE_PATH_RESULTS = "../data_results"

    # MODIFY THIS: Dataset's name
    filename_nodes = "dataset_3000_nodes_proteins.csv"
    filename_edges = "dataset_3000_edges_interactions.csv"

    # MODIFY THIS: File paths
    file_path_nodes = os.path.join(FILE_PATH_DATASETS, filename_nodes)
    file_path_edges = os.path.join(FILE_PATH_DATASETS, filename_edges)

    # ==============       DO NOT MODIFY THE REST OF THE CODE      ================
    # print metadata related to this script
    print_metadata(file_path_nodes, file_path_edges)

    # Define if you will profile the code with memray
    memray_is_used = False

    ###################     CODE UNDER TEST (START)     ########################
    if memray_is_used:
        memray_output_file = filename_edges.split("_")[1]
        memray_output_file = "memray_graph_" + memray_output_file + "_adjacency_map.bin"
        memray_file_path_results = os.path.join(FILE_PATH_RESULTS, memray_output_file)

        if os.path.exists(memray_file_path_results):
            os.remove(memray_file_path_results)

        with memray_tracker(memray_file_path_results):
            nodes_dict, edges_adjacency_map, graph = pipeline(
                file_path_nodes, file_path_edges
            )  # <-- Our code under test
    else:
        # Create a cProfiler
        profiler = Profile()
        profiler.enable()

        nodes_dict, edges_adjacency_map, graph = pipeline(
            file_path_nodes, file_path_edges
        )  # <-- Our code under test

        profiler.disable()

        # ==============       TIME STATS
        print("\n======   Time profile")
        stats = pstats.Stats(profiler).sort_stats("cumtime")
        stats.print_stats(30)

        # ==============       MEMORY STATS
        print("======   Memory profile")
        pympler_profiler(
            nodes=nodes_dict, edges=edges_adjacency_map, graph=graph, integer=10
        )

        # print("\nExample raw node:")
        # slice_nodes = dict(islice(nodes_dict.items(), 1))
        # print(dumps(slice_nodes, indent=4))

        # print("Example raw edges:")
        # slice_edges = dict(islice(edges_adjacency_map.items(), 1))
        # print(dumps(slice_edges, indent=4))

        example_info_networkx_graph(graph)

        print("\nEnd of report!!!")

    ####################     CODE UNDER TEST (END)      ########################
