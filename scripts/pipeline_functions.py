from ast import literal_eval
from collections import defaultdict
from csv import reader as csv_reader
from typing import (
    Any,
    DefaultDict,
    Dict,
    Generator,
    Iterator,
    Tuple,
)

import networkx as nx  # type: ignore
import numpy as np
import pandas as pd  # type: ignore


# ----------------------------------------------------------------
# -------------        General to the pipeline      --------------
# ----------------------------------------------------------------
def load_csv_generator(file_path: str, header: bool = True) -> Iterator[tuple]:
    """
    Reads a CSV file and yields each row as a tuple.

    This function reads a CSV file line by line, yielding each row as a tuple.
    If the `header` argument is set to `True`, the first row of the file is
    treated as a header and skipped.

    Args:
        file_path (str): The full path to the CSV file to be read.
        header (bool, optional): Whether to skip the first row of the file,
            assuming it contains column headers. Defaults to True.

    Yields:
        tuple: A tuple containing the values of a row in the CSV file.

    """
    with open(file_path, "r", encoding="utf8") as file:
        reader = csv_reader(file)
        if header:
            next(reader)
            header = False
        for row in reader:
            yield tuple(row)


def transform_node_tuple_to_two_fields(
    nodes_iterable: Iterator[Tuple[str, str, str]],
    mapping_properties: bool = True,
) -> Generator[Tuple[str, Dict], None, None]:
    """
    Transforms an iterable of node tuples into a new format, yielding tuples containing
    the node ID and properties as a dictionary (with optional modification).

        - Original format: (node_id, node_label, properties)
        - Transformed format: (node_id, properties), properties could include node_label
        inside.

    Args:
        nodes_iterable (Iterator[Tuple[str, str, str]]): An iterable of tuples where each tuple
            contains a node ID, node label, and a string representing the properties.
        mapping_properties (bool, optional): If True, adds the 'node_label' to the properties dictionary.
            Defaults to True.

    Yields:
        Generator[Tuple[str, str | Dict]]: A tuple containing the node id and the properties, which
            is either a dictionary (with optional modification) or a string if parsing fails.
    """
    for node_id, node_label, properties in nodes_iterable:
        try:
            properties_dict = literal_eval(properties)
        except ValueError as error:
            properties_dict = properties

        if mapping_properties and isinstance(properties_dict, dict):
            properties_dict["node_label"] = node_label

        yield (node_id, properties_dict)


def transform_edge_tuple_to_three_fields(
    edges_iterable: Iterator[Tuple[str, str, str, str, str]],
    mapping_properties: bool = True,
) -> Generator[Tuple[str, str, Dict], None, None]:
    """
    Transforms an iterable of edge tuples into a new format, yielding tuples containing
    the source ID, target ID, and properties as a dictionary (with optional modification).

    The input tuples have the format (edge_id, source_id, target_id, edge_label, properties).
    The output tuples have the format (source_id, target_id, properties), where 'properties'
    is a dictionary, and additional information can be added to it.

    Args:
        edges_iterable (Iterator[Tuple[str, str, str, str, str]]): An iterable of tuples
            where each tuple contains the edge's ID, source ID, target ID, edge label,
            and a string representation of properties (could be a dictionary in string form).
        mapping_properties (bool, optional): If True, adds the 'edge_id' and 'edge_label'
            to the properties dictionary. Defaults to True.

    Yields:
        Generator[Tuple[str, str, Dict], None, None]: A generator that yields tuples
            containing the source ID, target ID, and the properties as a dictionary.
            If `mapping_properties` is True, the properties will also include 'edge_id'
            and 'edge_label'.
    """

    for (
        edge_id,
        source_id,
        target_id,
        edge_label,
        properties,
    ) in edges_iterable:

        try:
            properties_dict = literal_eval(properties)
        except:
            properties_dict = properties

        if mapping_properties and isinstance(properties_dict, dict):
            properties_dict["edge_id"] = edge_id
            properties_dict["edge_label"] = edge_label

        yield (
            source_id,
            target_id,
            properties_dict,
        )


# ----------------------------------------------------------------
# -------------                LISTS                --------------
# ----------------------------------------------------------------
def create_lists(
    file_path_nodes, file_path_edges, header_nodes=True, header_edges=True
):

    nodes_ds = load_csv_generator(file_path_nodes, header=header_nodes)
    edges_ds = load_csv_generator(file_path_edges, header=header_edges)

    list_nodes = [item for item in nodes_ds]
    list_edges = [item for item in edges_ds]

    return list_nodes, list_edges


def networkx_graph_from_lists(
    nodes_iterable, edges_iterable, graph_type=nx.DiGraph()
):
    # Create an empty graph
    networkx_graph = graph_type

    # Populate the graph with edges and their properties
    networkx_graph.add_edges_from(edges_iterable)

    # Populate the graph with nodes and their properties
    networkx_graph.add_nodes_from(nodes_iterable)

    return networkx_graph


# ----------------------------------------------------------------
# -------------              PANDAS DF              --------------
# ----------------------------------------------------------------
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
        remaining_df = df.drop(
            columns=list(columns_to_keep_intact.keys()), axis=1
        )

    temp_dicts = pd.Series(
        [
            dict(zip(remaining_df.columns, row))
            for row in remaining_df.to_numpy()
        ],
        name="temp_dicts",
    )

    return pd.concat(
        [df.drop(columns=remaining_df.columns, axis=1), temp_dicts], axis=1
    )


def merge_properties(df, column_to_keep, column_to_merge):

    df[column_to_keep] = df[column_to_keep].map(literal_eval)
    df[column_to_keep] = [
        {**c1, **c2} for c1, c2 in zip(df[column_to_keep], df[column_to_merge])
    ]

    return df.drop(columns=column_to_merge, axis=1)


def change_column_names(df, column_names_dict):
    return df.rename(columns=column_names_dict)


def df_to_networkx_nodes(nodes_df, columns_to_keep_intact, column_names_dict):
    return (
        nodes_df.pipe(
            row_to_dictionary, columns_to_keep_intact=columns_to_keep_intact
        )
        .pipe(
            merge_properties,
            column_to_keep="properties",
            column_to_merge="temp_dicts",
        )
        .pipe(change_column_names, column_names_dict)
    )


def df_to_networkx_edges(edges_df, columns_to_keep_intact, column_names_dict):
    return (
        edges_df.pipe(
            row_to_dictionary, columns_to_keep_intact=columns_to_keep_intact
        )
        .pipe(merge_properties, "properties", "temp_dicts")
        .pipe(change_column_names, column_names_dict)
    )


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
                networkx_edges_df["properties"],
            ],
            axis=1,
        ).itertuples(index=False, name=None)
    )

    # populate_graph_nodes_properties
    networkx_graph.add_nodes_from(
        pd.concat(
            [
                networkx_nodes_df["source"],
                networkx_nodes_df["properties"],
            ],
            axis=1,
        ).itertuples(index=False, name=None)
    )
    return networkx_graph


# ----------------------------------------------------------------
# -------------             DICTIONARIES            --------------
# ----------------------------------------------------------------
def generate_nodes_dict(
    generator_nodes: Iterator[Tuple[str, Dict]]
) -> Dict[str, Dict]:
    """Creates a dictionary where each node is stored with its corresponding
    properties.
    Args:
        generator_nodes (Iterator[Tuple[str, Dict]]): An iterable of tuples,
            each containing a node ID (str) and its associated properties (dict).

    Returns:
        Dict[str, Dict]:  A dictionary where the keys are node IDs (str) and the
            values are the corresponding properties (dict).
    """
    return {node: properties for (node, properties) in generator_nodes}


def create_adjacency_map(
    generator_edges: Iterator[Tuple[str, str, Dict]]
) -> DefaultDict[str, Dict[str, Dict[str, Any]]]:
    """Create an adjacency map (a dictionary-based graph structure) to store
    the relationships given in an iterator of edges. Each tuple in the iterator
    should satisfy the following format (source_id, target_id, properties).

    Args:
        generator_edges (Iterator[Tuple[str, str, Dict]]): An iterable of tuples,
            each containing a source ID (str), target ID and its associated
            properties (dict).

    Returns:
        DefaultDict[str, Dict[str, Dict[str, Any]]]: An adjacency map data structure.
    """

    adjacency_map: DefaultDict[str, Dict[str, Dict[str, Any]]] = defaultdict(
        dict
    )

    for source_id, target_id, properties in generator_edges:
        adjacency_map[source_id][target_id] = properties

    return adjacency_map


def create_dictionaries(
    file_path_nodes: str, file_path_edges: str
) -> Tuple[Dict, Dict]:
    """Create two dictionaries, one containing nodes and another containing the
    adjacency map that stores the relationships (edges) between nodes.

    Args:
        file_path_nodes (str): complete path to the directory where nodes are stored
        file_path_edges (str): complete path to the directory where edges are stored

    Returns:
        Tuple[Dict, Dict]: return the nodes and edges dictionaries.
    """
    nodes_ds_input = load_csv_generator(file_path_nodes, header=True)
    nodes_ds_gen1 = transform_node_tuple_to_two_fields(nodes_ds_input)
    nodes_ds_gen2 = generate_nodes_dict(nodes_ds_gen1)

    edges_ds_input = load_csv_generator(file_path_edges, header=True)
    edges_ds_gen1 = transform_edge_tuple_to_three_fields(edges_ds_input)
    edges_ds_gen2 = create_adjacency_map(edges_ds_gen1)

    nodes_ds_output = nodes_ds_gen2
    edges_ds_output = edges_ds_gen2

    return nodes_ds_output, edges_ds_output


def networkx_graph_from_dicts(
    nodes_dictionary: Dict,
    adjacency_map: Dict,
    graph_type: nx.Graph = nx.DiGraph(),
) -> nx.Graph:
    """Create a NetworkX graph based on the nodes and edges data.

    Args:
        nodes_dictionary (Dict): a dictionary containing the nodes.
        adjacency_map (Dict): an adjacency map containing the edges
        graph_type (nx.Graph, optional): type of graph to be created. Defaults to nx.DiGraph().

    Returns:
        nx.Graph: A NetworkX graph defined by graph_type
    """
    # Create and populate graph using an adjacency map
    networkx_graph = nx.from_dict_of_dicts(
        adjacency_map, create_using=graph_type
    )

    # Populate nodes with properties
    networkx_graph.add_nodes_from(nodes_dictionary.items())

    return networkx_graph


# ----------------------------------------------------------------
# -------------             NUMPY ARRAYS            --------------
# ----------------------------------------------------------------
def create_arrays(file_path_nodes, file_path_edges):
    nodes_ds = load_csv_generator(file_path_nodes, header=True)
    nodes_ds = create_numpy_array(nodes_ds)

    edges_ds = load_csv_generator(file_path_edges, header=True)
    edges_ds = create_numpy_array(edges_ds)

    return nodes_ds, edges_ds


def create_numpy_array(iterable):
    return np.fromiter(iterable, dtype=object)


def networkx_graph_from_nparrays(
    nodes_nparray, edges_nparray, graph_type=nx.DiGraph()
):
    # Build an empty graph
    networkx_graph = graph_type

    # Populate the graph with edges containing properties
    networkx_graph.add_edges_from(edges_nparray)

    # Populate the graph with nodes containing properties
    networkx_graph.add_nodes_from(nodes_nparray)

    return networkx_graph
