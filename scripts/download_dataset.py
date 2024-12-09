import argparse
import os
from datetime import datetime
from zipfile import ZipFile

from requests import get
from tqdm import tqdm


def command_line_interface() -> argparse.Namespace:
    """Create a suitable Command Line Interface for executing a
    command with arguments, and options.

    Example: python download_dataset \
        --url <dataset's url> \
        --outputpath <folder to store the dataset> \
        --extract-files <y/n>

    Returns
    -------
        namespace object containing all the arguments, options,
        parameters from the command line.
    """
    ap = argparse.ArgumentParser(
        prog="download_dataset",
        description="Download a zip file containing datasets from a given",
    )

    ap.add_argument(
        "-filename",
        "--filename",
        help="Filename for the Zip file (must include extension .zip).",
        default="dataset" + "_" + str(datetime.now().strftime("%Y%m%d%H%M%S")) + ".zip",
    )

    ap.add_argument(
        "-o",
        "--output-path",
        help="path to image's output folder.",
        default="./data_examples",
    )

    ap.add_argument(
        "-del",
        "--delete-zip",
        help="delete the downloaded Zip file.",
        type=bool,
        default=False,
    )

    ap.add_argument(
        "-url",
        "--url-repository",
        help="Link to the Zip file on the repository.",
    )

    cli_args = ap.parse_args()

    return cli_args


def download(url_link, file_path):

    with open(file_path, "wb") as file:
        print("Downloading File: {}\t\t".format(os.path.basename(file_path)))
        with get(url_link, stream=True) as resource:
            resource.raise_for_status()
            total = int(resource.headers.get("content-length", 0))

            # tqdm has many interesting parameters. Feel free to experiment!
            tqdm_params = {
                "desc": url_link,
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


def unpack_dataset(file_path, output_dir, remove_zip=False):
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
    # Extract the content of the command line interface
    args = command_line_interface()
    print(args)
    url_repository = args.url_repository

    output_path_datasets = args.output_path
    filename = args.filename

    file_path = os.path.join(output_path_datasets, filename)

    # Download function
    download(url_link=url_repository, file_path=file_path)

    # Uncompress data
    if args.delete_zip:
        unpack_dataset(file_path, output_path_datasets, remove_zip=True)
    else:
        unpack_dataset(file_path, output_path_datasets, remove_zip=False)


if __name__ == "__main__":
    main()
