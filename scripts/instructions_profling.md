# Instruction profiling data structures

## Part 1. Prepare Environment with dependencies installed
1. Create a new Python environment to avoid corrupt any other Python environment or simply reuse a personal sandbox you have.

2. Activate the Python environment.

3. Install all the dependencies given in the `requirements.txt` file.

4. Navigate to the folder `scripts` from the root folder in this repository
```bash
cd ./scripts
```
## Part 2. Download the dataset (set of CSV files)
5. Download the dummy datasets for testing purposes, all of them are stored in Zenodo under the link:

- Link: https://zenodo.org/records/14327409

   You can navigate to the webpage or simply use the utility `dataset_downloader.py` by running the following:
   ```bash
   python dataset_downloader.py -x -d \
   https://zenodo.org/api/records/14327409/files-archive \
   ../data_examples \
   dummy_datasets_biocypher.zip
   ```
    The datasets will be downloaded, extracted and at the end the .Zip file automatically will be deleted.

## Part 3. Profiling

For our experiment, we are testing two variables: Memory footprint and time for each function that compose a pipeline. The pipeline simply consist of:

- reading a CSV file
- create a data structure to store the data
- create a NetworkX graph based on this data.

We are going to measure the behavior for different data structures. By the time of the creation of this document we have the following data structures:

- Lists of tuples for nodes and edges.
- Pandas Dataframes for nodes and edges.
- Dictionary for nodes and adjacency map (dictionary-based) for edges.
- Numpy arrays for nodes and edges.

### Scripts
> **_NOTE:_**  It is important to execute all the scripts from the folder `scripts`, by the time of creation of this file the code is not organized as a package.

To profile each pipeline depending on each data structure, open the corresponding script:

- Lists: `SC1_profiling_lists.py`
- Pandas Dataframes: `SC2_profiling_pandas_dataframes.py`
- Dictionaries: `SC3_profiling_adjacency_map.py`
- Numpy arrays: `SC4_profiling_numpy_arrays.py`

#### Instructions:
1. Open the corresponding script.
2. Navigate to the entry point of the script:
```python
if __name__ == "__main__":
```
3. Choose the profiler of interest:
   - **option 1**. Measure time with `cProfile` and memory footprint with `Pympler` at the same time. This is the most time consuming option.
   - **option 2**. Measure memory footprint with `Memray` only.
   - **option 3**. Measure time with `cProfile` only

4. Change the filename of each file for nodes and edges, for simplicity you just need to replace the number in both filenames. For instance: 300, 600, 1200, etc. Check your dataset.
