import subprocess


# Test if the CLI can correctly read and handle a URL argument
def test_cli_read_url():
    # Simulate running the CLI application with a URL argument
    url_test = "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-zip-file.zip"
    result = subprocess.run(
        [
            "python",
            "scripts/dataset_downloader.py",
            "-x",
            url_test,
            ".",
            "test.zip",
        ],
        capture_output=True,
        text=True,
    )

    # Check that the process exited successfully (return code 0)
    assert result.returncode == 0
