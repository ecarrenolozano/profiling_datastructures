import logging
import os
from cProfile import Profile
from io import StringIO
from typing import Dict, Tuple

import networkx as nx  # type: ignore
import pandas as pd  # type: ignore
from memray import Tracker as memray_tracker


from helper_functions import (  # type: ignore
    check_dataset_files,
    clear_console,
    create_flags_profilers,
    create_log_filepath,
    create_memray_file_path,
    info_networkx_graph,
    print_cprofile_stats,
    print_metadata,
    pympler_profiler,
    set_logger,
)
from pipeline_functions import (  # type: ignore
    create_dataframes,
    networkx_graph_from_pandas,
    df_to_networkx_nodes,
    df_to_networkx_edges,
)

# =====================================================================
# ==================         CONSTANTS & PATHS        =================
# =====================================================================
FILE_PATH_DATASETS = "../data_examples"
FILE_PATH_RESULTS = "../data_results"
FILE_PATH_LOGS = "../logs"


# =====================================================================
# ==================       Functions Pipeline        ==================
# =====================================================================
def pipeline(
    file_path_nodes: str, file_path_edges: str
) -> Tuple[pd.DataFrame, pd.DataFrame, nx.Graph]:
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

    return nodes_df, edges_df, graph


# =====================================================================
# ==================            MAIN Function        ==================
# =====================================================================
if __name__ == "__main__":
    # Instructions:
    #    1. Choose profiling options.
    #        - [1/default] Measure time with cProfile + Pympler (time intensive).
    #        - [2] Measure memory footprint with Memray.
    #        - [3] Measure time with cProfile
    #    2. Update the datasets paths.
    #
    #    3. If use Memray, a .bin file will be generated. To consult results
    #       execute:
    #       $ memray tree <file path to the .bin file>
    #
    #    4. Consult log files for results related to cProfile and Pympler if enabled

    # MODIFY THIS: Choose between 1,2 or 3. By default value 1 will be taken.
    option_profiler = 3

    # MODIFY THIS: Update datasets filenames
    filename_nodes = "dataset_3000_nodes_proteins.csv"
    filename_edges = "dataset_3000_edges_interactions.csv"

    # MODIFY THIS: File paths
    file_path_nodes = os.path.join(FILE_PATH_DATASETS, filename_nodes)
    file_path_edges = os.path.join(FILE_PATH_DATASETS, filename_edges)
    file_path_logs = create_log_filepath(
        FILE_PATH_LOGS, filename_nodes, ending_filename="pandas_dataframes"
    )

    # =============================================================================
    # ==============       DO NOT MODIFY THE REST OF THE CODE      ================
    # Set logger for the rest of the app
    set_logger(file_path_logs)
    logger = logging.getLogger(__name__)

    clear_console()
    print_metadata(
        file_path_nodes, file_path_edges, file_path_logs, name_script=__file__
    )
    check_dataset_files(file_path_nodes, file_path_edges)

    ###################     CODE UNDER TEST (START)     ########################
    use_memray, cprofile_pympler = create_flags_profilers(option_profiler)

    if use_memray:
        memray_file_path_results = create_memray_file_path(
            FILE_PATH_RESULTS, filename_edges
        )
        logger.info(f"Writing Memray results into: {memray_file_path_results}")

        # Delete if already exist
        if os.path.exists(memray_file_path_results):
            os.remove(memray_file_path_results)

        # MEMRAY: Our code under test (pipeline)
        with memray_tracker(memray_file_path_results):
            nodes_ds, edges_ds, graph = pipeline(
                file_path_nodes, file_path_edges
            )  # <-- Our code under test

        logger.info("End of report!!!")

    else:
        # Create a cProfiler
        profiler = Profile()
        profiler.enable()

        # CPROFILE: Our code under test (pipeline)
        nodes_ds, edges_ds, graph = pipeline(file_path_nodes, file_path_edges)

        profiler.disable()

        # ==============       TIME STATS CPROFILE
        print_cprofile_stats(profiler)

        if cprofile_pympler:
            # ==============       MEMORY STATS PYMPLER
            pympler_profiler(
                nodes=nodes_ds, edges=edges_ds, graph=graph, integer=10
            )

    # ==============       DATA STATS
    logger.info("======   Data stats")
    buffer = StringIO()
    logger.info("--- Dataframe for nodes (info)")
    nodes_ds.info(memory_usage="deep", buf=buffer)
    logger.info(buffer.getvalue())

    buffer.truncate(0)
    buffer.seek(0)
    logger.info("--- Dataframe for edges (info)")
    edges_ds.info(memory_usage="deep", buf=buffer)
    logger.info(buffer.getvalue())

    info_networkx_graph(graph)

    # example_info_networkx_graph(graph)

    logger.info("End of report!!!")
    ####################     CODE UNDER TEST (END)      ########################
