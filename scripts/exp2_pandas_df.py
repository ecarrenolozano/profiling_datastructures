import os

import pandas as pd
from pympler import asizeof

FILE_PATH_DATASETS = "../data_examples"


def csv_to_df(file_path):
    return pd.read_csv(file_path)


def main():

    file_name_edges = "dataset_30_edges_interactions.csv"
    file_name_nodes = "dataset_30_nodes_proteins.csv"

    file_path_edges = os.path.join(FILE_PATH_DATASETS, file_name_edges)
    file_path_nodes = os.path.join(FILE_PATH_DATASETS, file_name_nodes)

    data_structure_df_edges = csv_to_df(file_path_edges)
    data_structure_df_nodes = csv_to_df(file_path_nodes)

    print("###############   DataFrame.info(memory_usage='deep')")
    print("Info dataframe for EDGES:\n\t")
    print(data_structure_df_edges.info(memory_usage="deep"))
    print("Info dataframe for NODES:\n\t")
    print(data_structure_df_nodes.info(memory_usage="deep"))

    print("###############   DataFrame.memory_usage(index=True, deep=True)")
    print("MEM USAGE EDGES:\n\t")
    print(data_structure_df_edges.memory_usage(index=True, deep=True).sum())
    print("MEM USAGE NODES:\n\t")
    print(data_structure_df_nodes.memory_usage(index=True, deep=True).sum())

    print("###############   Pympler ")
    print(asizeof.asized(data_structure_df_edges, detail=0).format())
    print(asizeof.asized(data_structure_df_nodes, detail=0).format())


if __name__ == "__main__":
    main()
