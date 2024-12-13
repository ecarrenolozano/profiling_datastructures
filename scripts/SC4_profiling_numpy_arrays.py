import logging
import os
import platform
import pstats
from ast import literal_eval
from cProfile import Profile
from csv import reader as csv_reader

import networkx as nx
import numpy as np
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


def set_logger(log_file_path):
    # Create a logger
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()  # This will print to the console
    file_handler = logging.FileHandler(log_file_path, mode="w")  # This will log to a file

    # Set log levels for each handler
    console_handler.setLevel(logging.INFO)  # Print only INFO and higher to the console
    file_handler.setLevel(logging.DEBUG)  # Log DEBUG and higher to the file

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Attach formatter to handlers
    # console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


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
    sizes_megabytes = []
    for object in kwargs.keys():
        size_summary = asizeof.asized(kwargs[object], detail=0).format()

        total_size_megabytes = float(size_summary.split(" ")[-2].split("=")[1])
        total_size_megabytes /= 1e6

        flat_size_megabytes = float(size_summary.split(" ")[-1].split("=")[1])
        flat_size_megabytes /= 1e6

        sizes_megabytes.append(
            [
                object,
                type(kwargs[object]),
                total_size_megabytes,
                flat_size_megabytes,
            ]
        )

    return sizes_megabytes


def print_pympler_results(results):
    print(
        tabulate(
            results,
            headers=[
                "Variable",
                "object",
                "Total Size [MB]",
                "Flat Size [MB]",
            ],
        )
    )


def pympler_profiler(**kwargs):
    print("\nProfiling objects with Pympler...\n")
    results_pympler = profile_objects_pympler(**kwargs)
    print_pympler_results(results_pympler)


def info_networkx_graph(graph):
    logger.info("Number of nodes (NetworkX graph): {}".format(graph.number_of_nodes()))
    logger.info("Number of edges (NetworkX graph): {}".format(graph.number_of_edges()))


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


def create_arrays(file_path_nodes, file_path_edges):
    nodes_ds = load_csv_generator(file_path_nodes, header=True)
    nodes_ds = create_numpy_array(nodes_ds)

    edges_ds = load_csv_generator(file_path_edges, header=True)
    edges_ds = create_numpy_array(edges_ds)

    return nodes_ds, edges_ds


def create_numpy_array(iterable):
    return np.fromiter(iterable, dtype=object)


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


def networkx_graph_from_nparrays(nodes_nparray, edges_nparray, graph_type=nx.DiGraph()):
    # Build an empty graph
    networkx_graph = graph_type

    # Populate the graph with edges containing properties
    networkx_graph.add_edges_from(edges_nparray)

    # Populate the graph with nodes containing properties
    networkx_graph.add_nodes_from(nodes_nparray)

    return networkx_graph


def pipeline(file_path_nodes, file_path_edges):
    # Task 1. Create data structures for the internal representation
    nodes_nparray, edges_nparray = create_arrays(file_path_nodes, file_path_edges)

    # Task 2. Create a NetworkX graph based on the internal representation
    graph = networkx_graph_from_nparrays(
        nodes_nparray=to_networkx_nodes_format(nodes_nparray),
        edges_nparray=to_networkx_edges_format(edges_nparray),
        graph_type=nx.DiGraph(),
    )

    return nodes_nparray, edges_nparray, graph


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
    filename_nodes = "dataset_30000_nodes_proteins.csv"
    filename_edges = "dataset_30000_edges_interactions.csv"

    # MODIFY THIS: File paths
    file_path_nodes = os.path.join(FILE_PATH_DATASETS, filename_nodes)
    file_path_edges = os.path.join(FILE_PATH_DATASETS, filename_edges)

    log_file = filename_edges.split("_")[1]
    log_file = "log" + log_file + "_lists.log"
    log_file_path = os.path.join(FILE_PATH_RESULTS, log_file)

    logger = set_logger(log_file_path)

    # ==============       DO NOT MODIFY THE REST OF THE CODE      ================
    # print metadata related to this script
    print_metadata(file_path_nodes, file_path_edges)

    # Define if you will profile the code with memray
    memray_is_used = True

    ###################     CODE UNDER TEST (START)     ########################
    if memray_is_used:
        memray_output_file = filename_edges.split("_")[1]
        memray_output_file = "memray_graph_" + memray_output_file + "_numpy_arrays.bin"
        memray_file_path_results = os.path.join(FILE_PATH_RESULTS, memray_output_file)

        if os.path.exists(memray_file_path_results):
            os.remove(memray_file_path_results)

        with memray_tracker(memray_file_path_results):
            nodes_nparray, edges_nparray, graph = pipeline(
                file_path_nodes, file_path_edges
            )  # <-- Our code under test

    else:
        # Create a cProfiler
        profiler = Profile()
        profiler.enable()

        nodes_nparray, edges_nparray, graph = pipeline(
            file_path_nodes, file_path_edges
        )  # <-- Our code under test

        profiler.disable()

        # ==============       TIME STATS
        print("\n======   Time profile")
        stats = pstats.Stats(profiler).sort_stats("cumtime")
        stats.print_stats(30)

        # ==============       DATA STATS
        print("\n======   Data stats")
        print("Number of nodes(array): {}".format(nodes_nparray.size))
        print("Number of edges(array): {}".format(edges_nparray.size))

        info_networkx_graph(graph)

        print("\nExample raw nodes:\n\t{}".format(nodes_nparray[0:1]))
        print("Example raw edges:\n\t{}".format(edges_nparray[0:1]))

        example_info_networkx_graph(graph)

        # ==============       MEMORY STATS
        print("======   Memory profile")
        pympler_profiler(
            nodes=nodes_nparray, edges=edges_nparray, graph=graph, integer=10
        )

        print("NXEdges: {}".format(graph.number_of_edges()))
        print("NXNodes: {}".format(graph.number_of_nodes()))

        print("\nEnd of report!!!")
    ####################     CODE UNDER TEST (END)      ########################
