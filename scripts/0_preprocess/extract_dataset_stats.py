import click
import csv
from pathlib import Path


@click.command()
@click.option("--base-dir", default=Path().absolute(), type=click.Path(exists=True),
              help="Where the data and raw_data directories are located.")
def extract_dataset_stats(base_dir: Path):
    """Simple program that greets NAME for a total of COUNT times."""
    raw_data_dir = base_dir.joinpath("raw_data/hypertrie_node_stats")
    if not raw_data_dir.exists():
        click.echo("There must be a raw_data folder provided in the base-dir. "
                   "By default the current working directory is used. "
                   "You can use another base-dir by providing the cmd arg '--base-dir <path>'.",
                   err=True)
        exit(1)
    #  make output dir if it doesn't exist
    data_dir = base_dir.joinpath("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    output_file = data_dir.joinpath("dataset_stats.tsv")

    with open(output_file, "w", newline="") as f:
        csv_writer = csv.DictWriter(f,
                                    fieldnames=["dataset",
                                                "subjects",
                                                "predicates",
                                                "objects",
                                                "statements"],
                                    delimiter="\t")
        csv_writer.writeheader()
        for dataset in ["swdf", "dbpedia2015", "watdiv10000", "wikidata-2020-11-11"]:
            raw_data_file = raw_data_dir.joinpath(f"{dataset}").joinpath("depth_3_nodes_stats.tsv")
            with open(raw_data_file, "r", newline="") as input_file:
                csv_reader = csv.DictReader(input_file,
                                            delimiter="\t")
                line = next(csv_reader)
                csv_writer.writerow({
                    "dataset": f"{dataset}",
                    "subjects": line["dimension_1_size"],
                    "predicates": line["dimension_2_size"],
                    "objects": line["dimension_3_size"],
                    "statements": line["node_size"]
                })
    # todo: (optional) add number of queries


if __name__ == '__main__':
    extract_dataset_stats()
