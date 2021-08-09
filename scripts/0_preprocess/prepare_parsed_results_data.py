import click
import csv
from pathlib import Path
from typing import List, Optional


def transform_id(id: int, dataset: str, triplestore: str) -> Optional[int]:
    if ((triplestore == "fuseki" and dataset == 'wikidata-2020-11-11') or
            (triplestore == "fuseki-ltj")):
        return id
    else:
        excluded_queries = {
            "swdf": [],
            "dbpedia2015": [24, 33, 86, 91, 99, 103, 295],
            "watdiv10000": [],
            'wikidata-2020-11-11': [109, 235, 365, 451, 466],
        }
        assert dataset in excluded_queries
        excludes = excluded_queries[dataset]
        offset = 0
        for exclude in excludes:
            if id < exclude:
                break
            elif id == exclude:
                return None
            else:
                offset += 1
        return id - offset


def combine_csv_files(input_dir: Path, concatenated_csv_path: Path):
    with open(concatenated_csv_path, 'w') as concatenated_csv:
        csv_writer = None

        for input_csv in [file for file in input_dir.iterdir() if file.is_file() and file.suffix == ".csv"]:
            with open(input_csv, 'r') as input_file:
                csv_reader = csv.DictReader(input_file, )
                if csv_writer is None:
                    csv_writer = csv.DictWriter(concatenated_csv, fieldnames=csv_reader.fieldnames,
                                                quoting=csv.QUOTE_NONNUMERIC)
                    csv_writer.writeheader()
                for row in csv_reader:
                    id = transform_id(int(row["queryID"]), row["dataset"], row["triplestore"])
                    if id is not None:
                        row["queryID"] = str(id)
                        csv_writer.writerow(row)


@click.command()
@click.option("--base-dir", default=Path().absolute(), type=click.Path(exists=True),
              help="Where the data and raw_data directories are located.")
def prepare_parsed_results_data(base_dir: Path):
    """Simple program that greets NAME for a total of COUNT times."""
    raw_data_dir = base_dir.joinpath("raw_data/parsed_results")
    if not raw_data_dir.exists():
        click.echo("There must be a raw_data folder provided in the base-dir. "
                   "By default the current working directory is used. "
                   "You can use another base-dir by providing the cmd arg '--base-dir <path>'.",
                   err=True)
        exit(1)
    #  make output dir if it doesn't exist
    data_dir = base_dir.joinpath("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    output_file = data_dir.joinpath("parsed_results_stats.csv")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            from remove_rc_from_version import remove_rc_from_version
            remove_rc_from_version(raw_data_dir, Path(tmp_dir), '.csv')
            combine_csv_files(Path(tmp_dir), output_file)
        except Exception as ex:
            click.echo("Error encountered while processing files. \n"
                       "{}".format(ex),
                       err=True)
        else:
            click.echo(
                "Cleaned and concatenated file with parsing results was written to {}".format(output_file.absolute()))


if __name__ == '__main__':
    prepare_parsed_results_data()
