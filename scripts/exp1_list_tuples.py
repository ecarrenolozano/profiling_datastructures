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
            yield tuple(row)


def generate_lists(edges_generator, nodes_generator):
    list_edges = [item for item in edges_generator]
    list_nodes = [item for item in nodes_generator]

    return list_edges, list_nodes


def main():

    file_name_edges = "dataset_30_edges_interactions.csv"
    file_name_nodes = "dataset_30_nodes_proteins.csv"

    file_path_edges = os.path.join(FILE_PATH_DATASETS, file_name_edges)
    file_path_nodes = os.path.join(FILE_PATH_DATASETS, file_name_nodes)

    ds_list_edges, ds_list_nodes = generate_lists(
        load_csv_generator(file_path_edges), load_csv_generator(file_path_nodes)
    )

    print("Example:\n\t{}".format(ds_list_edges[0:1]))
    # print("Example:\n\t{}".format(ds_list_nodes[0:5]))

    print(asizeof.asized(ds_list_edges, detail=0).format())
    print(asizeof.asized(ds_list_nodes, detail=0).format())


if __name__ == "__main__":
    main()
