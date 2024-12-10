import os
from argparse import ArgumentParser
from zipfile import ZipFile

from requests import get
from tqdm import tqdm


def command_line_interface():
    """CLI Application for Downloading and Extracting Datasets


    A command-line tool for downloading datasets from specified URLs and
    extracting ZIP-compressed files. It streamlines data preparation by
    managing downloads, file extraction, and directory organization for
    seamless data analysis workflows

        Features:
        - Download datasets from provided internet links.
        - Automatically extract ZIP-compressed files.
        - Save files to a specified output directory or default to the current
        working directory.
        - Provide meaningful command-line help and error messages.


        Returns:
            args: a Namespace containing all the arguments and functions
            defined in this function.
    """

    cli_parser = ArgumentParser(
        prog="dataset_downloader",
        description="A command-line tool for downloading and extracting\
            datasets compressed in ZIP format from the internet.",
        epilog="Dev. team BioCypher project 2024",
    )

    general = cli_parser.add_argument_group("general output")

    general.add_argument("url_dataset", help="URL for the repository.")
    general.add_argument("output_dir", help="Download's folder for the file. ")
    general.add_argument("filename", help="Name for the downloaded Zip file.")

    detailed = cli_parser.add_argument_group("detailed output")
    detailed.add_argument("-x", "--extract-all", action="store_true")
    detailed.add_argument("-d", "--delete-zip", action="store_true")

    args = cli_parser.parse_args()

    return args


def download_dataset(url_dataset, output_dir, filename):
    """Download the collections of datasets in Zip format, into
    a specified output folder.

    Args:
        url_dataset (str): URL for the repository.
        output_dir (str): Download's folder for the file.
        filename (str): Name for the downloaded Zip file.
    Returns:
        None
    """
    file_path = os.path.join(output_dir, filename)

    try:
        with open(file_path, "wb") as file:
            print(
                "Downloading File: {} ......\t\t".format(
                    os.path.basename(file_path)
                )
            )
            with get(url_dataset, stream=True) as resource:
                resource.raise_for_status()
                total = int(resource.headers.get("content-length", 0))

                tqdm_params = {
                    "desc": url_dataset,
                    "total": total,
                    "miniters": 1,
                    "unit": "B",
                    "unit_scale": True,
                    "unit_divisor": 1024,
                }
                with tqdm(**tqdm_params) as progress_bar:
                    for chunk in resource.iter_content(chunk_size=8192):
                        progress_bar.update(len(chunk))
                        file.write(chunk)
    except FileNotFoundError:
        raise Exception(f"File {file_path} does not exist.")


def unpack_dataset(output_dir, filename, remove_zip=False):
    """Unpack Zip file and extract content (optional).

    Args:
        output_dir (str): Output directory where is store the Zip file.
        filename (str): Zip filename
        remove_zip (bool, optional): True if delete Zip file, False if keep
            Zip file. Defaults to False.

    Raises:
        Exception: FileNotFoundError
    """
    file_path = os.path.join(output_dir, filename)

    with ZipFile(file_path) as compressed_file:
        print("Unpacking files...")
        compressed_file.printdir()
        compressed_file.extractall(output_dir)

    if remove_zip:
        try:
            os.remove(file_path)
            print("{} has been removed!".format(os.path.basename(file_path)))
        except FileNotFoundError:
            raise Exception(f"File {file_path} does not exist.")


def main():
    # Parse arguments given in the CLI
    parser_args = command_line_interface()

    url_dataset = parser_args.url_dataset
    output_dir = parser_args.output_dir
    filename = parser_args.filename

    # Execute downloader
    download_dataset(
        url_dataset=url_dataset, output_dir=output_dir, filename=filename
    )

    # Extract and unpack files
    if parser_args.extract_all:
        remove_zip = parser_args.delete_zip
        unpack_dataset(output_dir, filename, remove_zip=remove_zip)


if __name__ == "__main__":
    main()
