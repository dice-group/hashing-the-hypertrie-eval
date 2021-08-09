from pathlib import Path


def remove_rc_from_version(input_dir: Path, output_dir: Path, file_suffix: str):
    """
    Copies files from input_dir to output dir. Tentris release candidate tags are removed from filenames and in the files.
    Only files with the given file_suffix are considered.
    """
    removed_substrings = [
        "rc14_",
        "rc15_",
        "-rc5",
        "-rc4",
    ]
    for input_file in [file for file in input_dir.iterdir() if file.is_file() and file.suffix == file_suffix]:

        output_name = input_file.name
        file_text = input_file.read_text()
        for substr in removed_substrings:
            # clear file name
            output_name = output_name.replace(substr, "")
            # clear file content
            file_text = file_text.replace(substr, "")

        # write output file
        output_file = output_dir.joinpath(output_name)
        output_file.write_text(file_text)
