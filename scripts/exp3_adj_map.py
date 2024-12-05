import ast
import csv
import os

from pympler import asizeof


FILE_PATH_DATASETS = "../data_examples"


def load_csv_generator(file_path, header=True):
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        if header:
            next(reader)
        for row in reader:
            row = [field.strip() for field in row]
            yield tuple(row)


def create_adjacency_map(edge_generator, node_generator):
    graph_dict = {"nodes": {}, "edges": {}}

    # populate edges dictionary
    for edge_id, source_id, target_id, edge_label, properties in edge_generator:
        # Add the source to the map if not already present
        if source_id not in graph_dict["edges"]:
            graph_dict["edges"][source_id] = {}
        # Add the destination to the source's adjacency set
        graph_dict["edges"][source_id][target_id] = ast.literal_eval(properties)

        # Optional: Uncomment the next lines for undirected graphs
        # if destination not in adjacency_map:
        #     adjacency_map[destination] = set()
        # adjacency_map[destination].add(source)

    for node_id, node_label, properties in node_generator:
        if node_id not in graph_dict["nodes"]:
            graph_dict["nodes"][node_id] = {}
        # Add the destination to the source's adjacency set
        graph_dict["nodes"][node_id] = ast.literal_eval(properties)

    return graph_dict


def main():

    # file_name_edges = "dataset_dummy2_edges.csv"
    # file_name_nodes = "dataset_dummy2_nodes.csv"

    file_name_edges = "dataset_30_edges_interactions.csv"
    file_name_nodes = "dataset_30_nodes_proteins.csv"

    file_path_edges = os.path.join(FILE_PATH_DATASETS, file_name_edges)
    file_path_nodes = os.path.join(FILE_PATH_DATASETS, file_name_nodes)

    data_structure = create_adjacency_map(
        edge_generator=load_csv_generator(file_path_edges, header=True),
        node_generator=load_csv_generator(file_path_nodes, header=True),
    )

    # print("Example:\n\t{}".format(data_structure.keys()))
    # J = nx.from_dict_of_dicts(data_structure["edges"], create_using=nx.DiGraph())

    # for node in data_structure['nodes'].keys():
    #    J.add_node(node, **data_structure['nodes'][node])

    # print(J.edges(data=True))
    # print(J.nodes(data=True))

    # print(asizeof.asized(data_structure, detail=0).format())


if __name__ == "__main__":
    main()
