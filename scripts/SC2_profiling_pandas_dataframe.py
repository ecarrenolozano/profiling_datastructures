import ast
import cProfile
import csv
import os
import platform
import pstats

import memray
import networkx as nx
import pandas as pd
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
        reader = csv.reader(file)
        if header:
            next(reader)
        for row in reader:
            yield tuple(row)


def from_csv_to_pandasdf(file_path, delimiter=","):
    return pd.read_csv(file_path, delimiter=delimiter)


def create_dataframes(file_path_nodes, file_path_edges):
    nodes_df = from_csv_to_pandasdf(file_path_nodes, delimiter=",")
    edges_df = from_csv_to_pandasdf(file_path_edges, delimiter=",")
    return nodes_df, edges_df


def row_to_dictionary(df, columns_to_keep_intact):
    if isinstance(columns_to_keep_intact, list):
        remaining_df = df.drop(columns=columns_to_keep_intact, axis=1)
    if isinstance(columns_to_keep_intact, dict):
        remaining_df = df.drop(columns=list(columns_to_keep_intact.keys()), axis=1)

    temp_dicts = pd.Series(
        [dict(zip(remaining_df.columns, row)) for row in remaining_df.to_numpy()],
        name="temp_dicts",
    )

    return pd.concat([df.drop(columns=remaining_df.columns, axis=1), temp_dicts], axis=1)


def merge_properties(df, column_to_keep, column_to_merge):

    df[column_to_keep] = df[column_to_keep].map(ast.literal_eval)
    df[column_to_keep] = [
        {**c1, **c2} for c1, c2 in zip(df[column_to_keep], df[column_to_merge])
    ]

    return df.drop(columns=column_to_merge, axis=1)


def change_column_names(df, column_names_dict):
    return df.rename(columns=column_names_dict)


def df_to_networkx_nodes(nodes_df, columns_to_keep_intact, column_names_dict):
    nodes_df_transformed = (
        nodes_df.pipe(row_to_dictionary, columns_to_keep_intact=columns_to_keep_intact)
        .pipe(merge_properties, column_to_keep="properties", column_to_merge="temp_dicts")
        .pipe(change_column_names, column_names_dict)
    )
    return nodes_df_transformed


def df_to_networkx_edges(edges_df, columns_to_keep_intact, column_names_dict):
    edges_df_transformed = (
        edges_df.pipe(row_to_dictionary, columns_to_keep_intact=columns_to_keep_intact)
        .pipe(merge_properties, "properties", "temp_dicts")
        .pipe(change_column_names, column_names_dict)
    )
    return edges_df_transformed


def networkx_graph_from_pandas(
    networkx_nodes_df, networkx_edges_df, graph_type=nx.DiGraph()
):
    # create an empty graph
    networkx_graph = graph_type

    # populate_graph_nodes_properties
    networkx_graph.add_edges_from(
        pd.concat(
            [
                networkx_edges_df[["source", "target"]],
                networkx_edges_df["properties"],  # .map(ast.literal_eval)
            ],
            axis=1,
        ).itertuples(index=False, name=None)
    )

    # populate_graph_nodes_properties
    networkx_graph.add_nodes_from(
        pd.concat(
            [
                networkx_nodes_df["source"],
                networkx_nodes_df["properties"],  # .map(ast.literal_eval)
            ],
            axis=1,
        ).itertuples(index=False, name=None)
    )
    return networkx_graph


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
    filename_nodes = "dataset_30_nodes_proteins.csv"
    filename_edges = "dataset_30_edges_interactions.csv"

    # MODIFY THIS: File paths
    file_path_nodes = os.path.join(FILE_PATH_DATASETS, filename_nodes)
    file_path_edges = os.path.join(FILE_PATH_DATASETS, filename_edges)

    # Define if you will profile the code with memray
    memray_is_used = True

    ###################     CODE UNDER TEST (START)     ########################
    if memray_is_used:
        memray_output_file = filename_edges.split("_")[1]
        memray_output_file = (
            "memray_graph_" + memray_output_file + "_pandas_dataframe.bin"
        )
        memray_file_path_results = os.path.join(FILE_PATH_RESULTS, memray_output_file)

        if os.path.exists(memray_file_path_results):
            os.remove(memray_file_path_results)

        with memray.Tracker(memray_file_path_results):
            # Task 1. Create data structures for the internal representation
            nodes_df, edges_df = create_dataframes(file_path_nodes, file_path_edges)

            # Task 2. Create a NetworkX graph based on the internal representation
            # Dictionaries to change the name of columns to maintain compatibility with Networkx
            columns_names_nodes = {"UniProt ID": "source", "properties": "properties"}

            columns_names_edges = {
                "Source ID": "source",
                "Target ID": "target",
                "properties": "properties",
            }

            graph = networkx_graph_from_pandas(
                networkx_nodes_df=df_to_networkx_nodes(
                    nodes_df,
                    columns_to_keep_intact=["UniProt ID", "properties"],
                    column_names_dict=columns_names_nodes,
                ),
                networkx_edges_df=df_to_networkx_edges(
                    edges_df,
                    columns_to_keep_intact=["Source ID", "Target ID", "properties"],
                    column_names_dict=columns_names_edges,
                ),
                graph_type=nx.DiGraph(),
            )
    else:
        # Create a cProfiler
        profiler = cProfile.Profile()
        profiler.enable()

        # Task 1. Create data structures for the internal representation
        nodes_df, edges_df = create_dataframes(file_path_nodes, file_path_edges)

        # Task 2. Create a NetworkX graph based on the internal representation
        # Dictionaries to change the name of columns to maintain compatibility with Networkx
        columns_names_nodes = {"UniProt ID": "source", "properties": "properties"}

        columns_names_edges = {
            "Source ID": "source",
            "Target ID": "target",
            "properties": "properties",
        }

        graph = networkx_graph_from_pandas(
            networkx_nodes_df=df_to_networkx_nodes(
                nodes_df,
                columns_to_keep_intact=["UniProt ID", "properties"],
                column_names_dict=columns_names_nodes,
            ),
            networkx_edges_df=df_to_networkx_edges(
                edges_df,
                columns_to_keep_intact=["Source ID", "Target ID", "properties"],
                column_names_dict=columns_names_edges,
            ),
            graph_type=nx.DiGraph(),
        )

        profiler.disable()

        # ==============       TIME STATS
        print("\n======   Time profile")
        stats = pstats.Stats(profiler).sort_stats("cumtime")
        stats.print_stats(30)

        # ==============       MEMORY STATS
        print("======   Memory profile")
        pympler_profiler(nodes=nodes_df, edges=edges_df, integer=10)

        print("\nExample raw nodes:\n\t{}".format(nodes_df[0:1]))
        print("Example raw edges:\n\t{}".format(edges_df[0:1]))

        example_info_networkx_graph(graph)

        print("\nEnd of report!!!")
    ####################     CODE UNDER TEST (END)      ########################
