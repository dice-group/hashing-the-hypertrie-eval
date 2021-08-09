import subprocess
import click
import csv
from pathlib import Path
from typing import List, Optional

iguana_file_prefixes = """
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix imetric: <http://iguana-benchmark.eu/class/metric/> .
@prefix iprop: <http://iguana-benchmark.eu/properties/> .
@prefix iont:  <http://iguana-benchmark.eu/class/> .
@prefix ires:  <http://iguana-benchmark.eu/resource/> .
@prefix lsqr:  <http://lsq.aksw.org/res/> .
"""


def combine_rdf_files(input_dir: Path, combined_ttl: Path):
    tmp_combined_ttl_path = input_dir.joinpath("benchmarking_results_tmp.ttl")

    with open(tmp_combined_ttl_path, 'w') as combined_nt:
        for input_nt in [file for file in input_dir.iterdir() if file.is_file() and file.suffix == ".nt"]:
            with open(input_nt, 'r') as input_file:
                for line in input_file:
                    combined_nt.write(line)

    tmp_prefixes_ttl_path = input_dir.joinpath("iguana_prefixes_tmp.ttl")
    tmp_prefixes_ttl_path.write_text(iguana_file_prefixes)

    subprocess.check_call(['/bin/bash', '-i', '-c',
                           'sort "{tmp_ttl}" | uniq >> "{tmp_ttl}"'.format(tmp_ttl=tmp_combined_ttl_path.absolute())],
                          stderr=subprocess.PIPE)
    subprocess.check_call(['/bin/bash', '-i', '-c',
                           'cat "{tmt_prefixes}" "{tmp_ttl}" | riot --syntax=TURTLE --output=TURTLE > "{file_path}"'
                          .format(tmt_prefixes=tmp_prefixes_ttl_path.absolute(),
                                  tmp_ttl=tmp_combined_ttl_path.absolute(),
                                  file_path=combined_ttl.absolute())
                           ],
                          stderr=subprocess.PIPE)


@click.command()
@click.option("--base-dir", default=Path().absolute(), type=click.Path(exists=True),
              help="Where the data and raw_data directories are located.")
def prepare_benchmarking_data(base_dir: Path):
    """Simple program that greets NAME for a total of COUNT times."""
    raw_data_dir = base_dir.joinpath("raw_data/benchmarking_results")
    if not raw_data_dir.exists():
        click.echo("There must be a raw_data folder provided in the base-dir. "
                   "By default the current working directory is used. "
                   "You can use another base-dir by providing the cmd arg '--base-dir <path>'.",
                   err=True)
        exit(1)
    #  make output dir if it doesn't exist
    data_dir = base_dir.joinpath("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    output_file_ttl = data_dir.joinpath("benchmarking_results.ttl")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            from remove_rc_from_version import remove_rc_from_version
            remove_rc_from_version(raw_data_dir, Path(tmp_dir), ".nt")
            combine_rdf_files(Path(tmp_dir), output_file_ttl)
        except Exception as ex:
            click.echo("Error encountered while processing files. \n"
                       "{}".format(ex),
                       err=True)
            exit(1)
        click.echo(
            "Concatenated rdf file with benchmarking results was written to {}".format(output_file_ttl.absolute()))

        output_file_csv = data_dir.joinpath("benchmarking_results.csv")

        try:
            i2c_dir = Path(tmp_dir).joinpath("iguanaresult2csv")
            i2c_dir.mkdir(parents=True, exist_ok=True)
            output_each_query_csvs: List[Path] = list()
            import iguanaresult2csv.processing
            from iguanaresult2csv.exec import run
            click.echo("Extracted csvs:")
            for output_files in iguanaresult2csv.processing.convert_result_file(output_file_ttl, i2c_dir):
                assert (output_files[2])
                click.echo("  {}".format(output_files[2].name))
                output_each_query_csvs.append(output_files[2])
            run.combine_csv_files(output_file_csv, output_each_query_csvs)
        except Exception as ex:
            click.echo("Error encountered while processing files. \n"
                       "{}".format(ex),
                       err=True)
            exit(1)
        click.echo(
            "Concatenated csv file with benchmarking results was written to {}".format(output_file_csv.absolute()))
        exit(0)


if __name__ == '__main__':
    prepare_benchmarking_data()
