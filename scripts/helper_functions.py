import io
import logging
import os
import pstats
from socket import gethostname
from typing import List
from typing import Tuple

from platform import system as platform_system
from pympler import asizeof
from tabulate import tabulate


def create_log_filepath(file_path_logs, filename_nodes, ending_filename):
    log_file_name = filename_nodes.split("_")[1]
    logger.info(filename_nodes)
    log_file_name = "log_" + log_file_name + "_" + ending_filename + ".log"
    log_file_path = os.path.join(file_path_logs, log_file_name)

    return log_file_path


def set_logger(log_file_path):
    """Create and configure a logger that outputs log messages to both a file
    and the console.

    Args:
        log_file_path (str): file path where the messages will be stored.

    Returns:
        logging.Logger: A configured logger that writes log messages to a file
        and show execution in terminal.
    """

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()  # Handler to output in console
    file_handler = logging.FileHandler(
        log_file_path, mode="a"
    )  # Handler to log to a file

    # Set log levels for each handler
    console_handler.setLevel(
        logging.INFO
    )  # Print only INFO and higher to the console
    file_handler.setLevel(logging.INFO)  # Log DEBUG and higher to the file

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Attach formatter to handlers
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def clear_console() -> None:
    """Clear the console when executed"""
    if platform_system() == "Windows":
        os.system("cls")  # Windows
    else:
        os.system("clear")  # Unix/Linux/MacOS


def print_metadata(
    file_path_nodes: str,
    file_path_edges: str,
    file_path_logs: str,
    name_script,
) -> None:
    """Print a header indicating the start of the current script. Name of the current
    script and paths to the datasets (nodes and edges) are indicated.

    Args:
        file_path_nodes (str): complete path to the nodes dataset
        file_path_edges (str): complete path to the edges dataset
        file_path_logs (str): complete path to logs folder dataset
    """
    logger.info(
        "--------------------------------------------------------------------"
    )
    logger.info(
        "------------------       Profiling Pipeline       ------------------"
    )
    logger.info(
        "--------------------------------------------------------------------"
    )
    logger.info(f"Machine (hostname): {gethostname()}")
    logger.info("Metadata")

    logger.info(
        "\t\tScript's name:\t\t{}".format(os.path.basename(name_script))
    )
    logger.info("\t\tData for nodes (path):\t{}".format(file_path_nodes))
    logger.info("\t\tData for edges (path):\t{}".format(file_path_edges))
    logger.info("\t\tLogs path:\t\t{}\n".format(file_path_logs))


def check_dataset_files(file_path_nodes, file_path_edges):
    if not os.path.exists(file_path_nodes):
        logger.error(f"File doesn't exist: {file_path_nodes}")
    if not os.path.exists(file_path_edges):
        logger.error(f"File doesn't exist: {file_path_edges}")


def create_flags_profilers(option: int = 1):
    match option:
        case 1:
            logger.info(f"Profiling with cProfile + Pympler")
            use_memray = False
            cprofile_pympler = True

        case 2:
            logger.info(f"Profiling with Memray")
            use_memray = True
            cprofile_pympler = False
        case 3:
            logger.info(f"Profiling with cProfile only")
            use_memray = False
            cprofile_pympler = False
        case _:
            logger.info(f"Profiling with cProfile + Pympler")
            use_memray = False
            cprofile_pympler = True

    return use_memray, cprofile_pympler


def create_memray_file_path(file_path_results, filename_edges):
    memray_output_file = filename_edges.split("_")[1]
    memray_output_file = (
        "memray_graph_" + memray_output_file + "_adjacency_map.bin"
    )
    memray_file_path_results = os.path.join(
        file_path_results, memray_output_file
    )

    return memray_file_path_results


def print_cprofile_stats(profiler):
    stream = io.StringIO()
    logger.info("======   Time profile")
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumtime")
    stats.print_stats(30)
    logger.info(stream.getvalue())


def pympler_profiler(**kwargs):
    """
    Profiles the memory usage of objects using Pympler and logs the results.

    This function accepts keyword arguments representing the objects to be profiled.
    It uses Pympler to calculate memory usage details for each object and logs the
    profiling results in a tabular format.

    Args:
        **kwargs: Arbitrary keyword arguments where each key is the name of an object
                  and each value is the object to be profiled.

    Returns:
        None: This function does not return any value. It logs the profiling process
              and outputs a formatted table of results.

    Example:
        >>> my_list = [1, 2, 3]
        >>> my_dict = {"a": 1, "b": 2}
        >>> pympler_profiler(my_list=my_list, my_dict=my_dict)
        [Logs]
        Profiling objects with Pympler...
        +-----------+--------+-------------------+-------------------+
        | Variable  | object | Total Size [MB]   | Flat Size [MB]    |
        +-----------+--------+-------------------+-------------------+
        | my_list   | list   | 0.0000012         | 0.0000012         |
        | my_dict   | dict   | 0.0000035         | 0.0000035         |
        +-----------+--------+-------------------+-------------------+

    Notes:
        - This function depends on two other functions:
            - `profile_objects_pympler`: Profiles the memory usage of the objects.
            - `print_pympler_results`: Formats and logs the profiling results.
        - Ensure that the Pympler library is installed and properly set up.
        - A logger must be configured in the environment for logging to work correctly.
    """
    logger.info("======   Memory profile with Pympler")
    logger.info("Profiling objects with Pympler...")
    results_pympler = profile_objects_pympler(**kwargs)
    print_pympler_results(results_pympler)


def profile_objects_pympler(**kwargs):
    """
    Calculate the size in megabytes of each object passed in the keyword arguments.

    Args:
        **kwargs: Arbitrary keyword arguments where each key represents the name of an object
                  and each value is the object whose size is to be calculated.

    Returns:
        list: A list of lists, each containing the following items:
            - 'name_object' (str): The name of the object (key in kwargs).
            - 'type' (str): The type of the object.
            - 'total_size' (float): The total size of the object in megabytes.
            - 'flat_size' (float): The flat size of the object in megabytes.
    """
    sizes_megabytes = []
    for object in kwargs.keys():
        size_summary = asizeof.asized(kwargs[object], detail=0).format()

        total_size_megabytes = float(size_summary.split(" ")[-2].split("=")[1])
        total_size_megabytes /= 1000**2

        flat_size_megabytes = float(size_summary.split(" ")[-1].split("=")[1])
        flat_size_megabytes /= 1000**2

        sizes_megabytes.append(
            (
                object,
                type(kwargs[object]),
                total_size_megabytes,
                flat_size_megabytes,
            )
        )

    return sizes_megabytes


def print_pympler_results(
    results: List[Tuple[str, str, float, float]]
) -> None:
    """
    Prints the memory size information of variables in a formatted table using the `tabulate` library.

    Args:
        results (_type_): _description_
    """
    logger.info(
        "size of variables: \n"
        + tabulate(
            results,
            headers=[
                "Variable",
                "object",
                "Total Size [MB]",
                "Flat Size [MB]",
            ],
            tablefmt="grid",
        )
    )


def info_networkx_graph(graph):
    logger.info(
        "\tNumber of nodes (NetworkX graph): {}".format(
            graph.number_of_nodes()
        )
    )
    logger.info(
        "\tNumber of edges (NetworkX graph): {}".format(
            graph.number_of_edges()
        )
    )


def example_info_networkx_graph(graph):
    limit = 2
    print("\n")
    logger.info("Example NetworkX nodes:")
    for index, node in enumerate(graph.nodes(data=True)):
        if index == limit:
            break
        logger.info(node)

    print("\n")
    logger.info("Example NetworkX edges:")
    for index, edge in enumerate(graph.edges(data=True)):
        if index == limit:
            break
        logger.info(edge)


logger = logging.getLogger(__name__)
