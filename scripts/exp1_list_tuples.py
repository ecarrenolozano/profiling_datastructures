import cProfile
import csv
import os
import pstats

from pympler import asizeof
from tabulate import tabulate


FILE_PATH_DATASETS = "../../../DATASETS"


# ----------------  HELPER FUNCTIONS
def profile_objects_pympler(**kwargs):
    sizes_mebibytes = []
    for object in kwargs.keys():
        size_summary = asizeof.asized(kwargs[object], detail=0).format()
        total_size_mebibytes = float(
            size_summary.split(" ")[-2].split("=")[1]
        ) / (1024**2)

        flat_size_mebibytes = float(
            size_summary.split(" ")[-1].split("=")[1]
        ) / (1024**2)

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


def generate_lists(nodes_generator, edges_generator):
    list_nodes = [item for item in nodes_generator]
    list_edges = [item for item in edges_generator]

    return list_nodes, list_edges


# ----------------  MAIN FUNCTION
def main():

    file_name_nodes = "dataset_300_nodes_proteins.csv"
    file_name_edges = "dataset_300_edges_interactions.csv"

    file_path_nodes = os.path.join(FILE_PATH_DATASETS, file_name_nodes)
    file_path_edges = os.path.join(FILE_PATH_DATASETS, file_name_edges)

    # ------------------  TIME STATS  -------------------------
    print("======   Time profile")
    # Create a cProfiler
    profiler = cProfile.Profile()
    profiler.enable()

    ds_list_nodes, ds_list_edges = generate_lists(
        load_csv_generator(file_path_nodes),
        load_csv_generator(file_path_edges),
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
