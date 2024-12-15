from ast import literal_eval
from typing import Generator, Union, Dict, List


# --- Static Transformation Methods


def node_to_format_two_fields(
    nodes_iterable: Generator, mapping_properties: bool = True
) -> Generator[tuple, None, None]:
    for node_id, node_label, properties in nodes_iterable:
        properties = literal_eval(properties)
        if mapping_properties:
            properties["node_label"] = node_label
        yield (node_id, properties)


def edge_to_format_three_fields(
    edges_iterable: Generator, mapping_properties: bool = True
) -> Generator[tuple, None, None]:
    for (
        edge_id,
        source_id,
        target_id,
        edge_label,
        properties,
    ) in edges_iterable:
        try:
            properties = literal_eval(properties)
        except ValueError:
            raise ValueError("Malformed properties string")

        if mapping_properties:
            properties["edge_id"] = edge_id
            properties["edge_label"] = edge_label

        yield (source_id, target_id, properties)
