from pathlib import Path

import janitor
from dfply import *
import click


def percentile(n):
    def percentile_(x):
        return x.quantile(n)

    percentile_.__name__ = 'percentile_{:2.0f}'.format(n * 100)
    return percentile_


descriptive_stats = ["mean",
                     "std",
                     "min",
                     percentile(.25),
                     "median",
                     percentile(.75),
                     "max"]

@click.command()
@click.option("--base-dir", default=Path().absolute(), type=click.Path(exists=True),
              help="Where the data and raw_data directories are located.")
def combine_data(base_dir: Path):
    data_dir = base_dir.joinpath("data")
    if not data_dir.exists():
        click.echo("There must be a data folder provided in the base-dir. "
                   "By default the current working directory is used. "
                   "You can use another base-dir by providing the cmd arg '--base-dir <path>'.",
                   err=True)
        exit(1)

    iguana_results = data_dir.joinpath("benchmarking_results.csv")
    parsing_results = data_dir.joinpath("parsed_results_stats.csv")

    iguana_data: pd.DataFrame = pd.DataFrame(pd.read_csv(iguana_results)).convert_dtypes()
    parsing_data: pd.DataFrame = pd.DataFrame(pd.read_csv(parsing_results)).convert_dtypes()

    formats = iguana_data["format"].unique()
    datasets = iguana_data["dataset"].unique()
    triplestores = iguana_data["triplestore"].unique()
    noclients_s = iguana_data["noclients"].unique()
    mixes = iguana_data["run"].max()

    join_columns = ['triplestore', 'dataset', "queryID", "contentLength"]
    parsing_columns = ['parsingSucceeded', 'numberOfVariables', 'numberOfSolutions',
                       'numberOfBindings', 'resultParsingTime', 'parsingErrorMessage']
    stats_columns = ['qps', 'penalizedQPS', 'succeeded', 'failed', 'timeouts', 'unknownExceptions', 'wrongCodes',
                     'time', 'contentLength', 'penalizedTime']
    aggregate_columns = ['triplestore', 'dataset', 'queryID']

    iguana_data >>= left_join(parsing_data[join_columns + parsing_columns], by=join_columns)

    iguana_data["parsingSucceeded"] = ~ iguana_data["parsingSucceeded"].isna()

    correct_result_sizes = []
    for dataset in datasets:
        tmp_ds = iguana_data.query(f'dataset == "{dataset}"')
        for queryID in tmp_ds.queryID.unique():
            tmp_qid = tmp_ds.query(f'queryID == {queryID} and (not numberOfSolutions.isna()) and succeeded')

            if tmp_qid.empty:
                correct_result_sizes.append(
                    {'dataset': dataset, 'queryID': queryID, 'numberOfSolutions': np.nan, 'numberOfBindings': np.nan,
                     'non_tentris_sparql': False})
            else:

                max_nos = tmp_qid.numberOfSolutions.max()
                n_nos = tmp_qid.numberOfSolutions.nunique()

                max_nob = tmp_qid.numberOfBindings.max()
                n_nob = tmp_qid.numberOfBindings.nunique()

                if n_nos == 1 and n_nob == 1:
                    correct_result_sizes.append(
                        {'dataset': dataset, 'queryID': queryID, 'numberOfSolutions': max_nos, 'numberOfBindings': max_nob,
                         'non_tentris_sparql': False})
                else:
                    fuseki_solutions = tmp_qid.query("triplestore == 'fuseki'")
                    fuseki_has_result = not fuseki_solutions.empty
                    if fuseki_has_result:
                        max_nos = fuseki_solutions.numberOfSolutions.max()
                        max_nob = fuseki_solutions.numberOfBindings.max()

                        fuseki_max_nos_idx = np.argmax(fuseki_solutions.numberOfSolutions)
                        fuseki_solution = fuseki_solutions.iloc[fuseki_max_nos_idx]
                        assert (fuseki_solution.numberOfSolutions == max_nos)
                        assert (fuseki_solution.numberOfBindings == max_nob)

                    solutions = []

                    tentris_versions = list(filter(lambda x: x.startswith("tentris"), tmp_qid.triplestore.unique()))
                    excluded_tentris_versions = set()
                    tentris_has_solution = False
                    if tentris_versions:
                        tentris_version = sorted(tentris_versions, reverse=True)[0]
                        excluded_tentris_versions = tentris_versions.copy()
                        excluded_tentris_versions.remove(tentris_version)
                        triplestore_solutions = tmp_qid.query(f"(triplestore == '{tentris_version}')")
                        tentris_has_solution = not triplestore_solutions.empty
                        if tentris_has_solution:
                            tentris_nos = triplestore_solutions.numberOfSolutions.max()
                            tentris_nob = triplestore_solutions.numberOfBindings.max()

                            tentris_max_nos_idx = np.argmax(triplestore_solutions.numberOfSolutions)
                            tentris_solution = triplestore_solutions.iloc[tentris_max_nos_idx]
                            assert (tentris_solution.numberOfSolutions == tentris_nos)
                            assert (tentris_solution.numberOfBindings == tentris_nob)
                            solutions.append(tentris_solution)

                    if not fuseki_has_result:
                        one_tentris_only = tmp_qid
                        one_tentris_only = one_tentris_only.query("triplestore not in @excluded_tentris_versions")

                        for triplestore in triplestores:
                            if triplestore in tentris_versions or triplestore == "fuseki":
                                continue
                            triplestore_solutions = tmp_qid.query(f"(triplestore == '{triplestore}')")
                            if not triplestore_solutions.empty:
                                nos = triplestore_solutions.numberOfSolutions.max()
                                nob = triplestore_solutions.numberOfBindings.max()

                                max_nos_idx = np.argmax(triplestore_solutions.numberOfSolutions)
                                solution = triplestore_solutions.iloc[max_nos_idx]
                                assert (solution.numberOfSolutions == nos)
                                assert (solution.numberOfBindings == nob)
                                solutions.append(solution)
                        if solutions:
                            solutions = pd.DataFrame.from_records(solutions)
                            max_nos, max_nob = solutions[['numberOfSolutions', 'numberOfBindings']].value_counts().index[
                                0]
                        else:
                            assert (False)

                    non_tentris_sparql = tentris_has_solution and not (
                            (tentris_nos == 1 and (tentris_nob == 0)) <= (max_nos == 1 and max_nob == 0))

                    correct_result_sizes.append(
                        {'dataset': dataset, 'queryID': queryID, 'numberOfSolutions': max_nos, 'numberOfBindings': max_nob,
                         'non_tentris_sparql': non_tentris_sparql})

    correct_result_sizes = pd.DataFrame(correct_result_sizes,
                                        columns=['dataset', 'queryID', 'numberOfSolutions', 'numberOfBindings',
                                                 'non_tentris_sparql']).convert_dtypes()
    correct_result_sizes.to_csv(data_dir.joinpath("result_stats_ground_truth.csv").absolute())

    exclude = {dataset: [] for dataset in datasets}

    for dataset, ex_qids in exclude.items():
        ex_qids.extend(
            correct_result_sizes.query(f"(dataset == '{dataset}') and (non_tentris_sparql == True)").queryID.unique()
        )

    # Filter out the queries which are not relevant
    for dataset, ex_qids in exclude.items():
        iguana_data = iguana_data.query(f"not (dataset == '{dataset}') or (queryID not in @ex_qids)")


    def np_encoder(object):
        if isinstance(object, np.generic):
            return object.item()


    import json

    excluded_queries_file = data_dir.joinpath("exclude_queries.json")
    with open(excluded_queries_file, 'w') as file:
        json.dump(exclude, file, default=np_encoder)


    x = iguana_data >> left_join(
        correct_result_sizes >> rename(numberOfSolutions_corr='numberOfSolutions',
                                       numberOfBindings_corr='numberOfBindings'),
        on=['dataset', 'queryID']
    )

    x['wrongResult'] = (
            (# not close to correct number of solutions
            (~np.isclose(x.numberOfSolutions.astype('float64'), x.numberOfSolutions_corr.astype('float64'),
                         rtol=0.1) | ~np.isclose(x.numberOfBindings.astype('float64'),
                                                 x.numberOfBindings_corr.astype('float64'), rtol=0.1))
            &
            # not less than ten solutions
            ~(
                    (np.less_equal(x.numberOfSolutions, 10) & np.greater_equal(x.numberOfSolutions,
                                                                               0) & np.less_equal(
                        x.numberOfSolutions_corr, 10) & np.greater_equal(x.numberOfSolutions_corr, 0)) &
                    (x.numberOfBindings == x.numberOfBindings_corr)
            ))
    )


    x["wrongResult"] = x["wrongResult"].fillna(False)
    x['fully_correct_result'] = (x.numberOfSolutions == x.numberOfSolutions_corr) & (
            x.numberOfBindings == x.numberOfBindings_corr)
    x['succeeded'] = (x.succeeded & ~x.wrongResult).astype(np.int64)
    x.drop(columns=["numberOfSolutions_corr", "numberOfBindings_corr"], inplace=True)
    x.convert_dtypes()
    x.loc[x.succeeded == False, ['time', 'qps']] = None
    iguana_data = x
    del x
    iguana_data.to_csv(data_dir.joinpath("benchmarking_results_with_result_stats.csv").absolute())

    iguana_data_agg = janitor.collapse_levels(
        iguana_data.drop(columns=['starttime', 'benchmarkID', 'format', 'run'])
            .groupby(['triplestore', 'dataset', 'queryID', 'clientID'], as_index=False) \
            .agg({
            **{'qps': descriptive_stats,
               'penalizedQPS': descriptive_stats,
               'time': descriptive_stats,
               'penalizedTime': descriptive_stats,
               },
            **{str(name): np.max for name in
               ['contentLength', 'numberOfSolutions', 'numberOfBindings', 'wrongResult', 'fully_correct_result',
                'parsingSucceeded']},
            **{str(name): np.sum for name in
               ['succeeded', 'failed', 'timeouts', 'unknownExceptions', 'wrongCodes']}
        })
    )
    iguana_data_agg.rename(columns={name + "_amax": name for name in
                                    ['contentLength', 'numberOfSolutions', 'numberOfBindings', 'wrongResult',
                                     'fully_correct_result', 'parsingSucceeded']}, inplace=True)
    iguana_data_agg.rename(columns={name + "_sum": name for name in
                                    ['succeeded', 'failed', 'timeouts', 'unknownExceptions', 'wrongCodes']}, inplace=True)
    iguana_data_agg.wrongResult = iguana_data_agg.apply(
        lambda x: ~bool(x.succeeded) & x.wrongResult, axis=1).values
    iguana_data_agg.to_csv(data_dir.joinpath("benchmarking_results_with_result_stats_agg.csv").absolute())

if __name__ == '__main__':
    combine_data()