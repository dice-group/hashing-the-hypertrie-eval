<meta name="robots" content="noindex">

# Hashing the Hypertrie: Space- and Time-Efficient Indexing for SPARQL in Tensors
## Evaluation of Results

Unzip the archive [`hashing_the_hypertrie_evaluation_results.zip`](./hashing_the_hypertrie_evaluation_results.zip) to extract the data produced during benchmarking, evaluation results and plots.

### Data

1. [`data/benchmarking_results.rdf`](./data/benchmarking_results.rdf) contains the results of all benchmarks executed with IGUANA.
2. [`data/benchmarking_results.csv`](./data/benchmarking_results.csv) contains the data of (1) converted to CSV.
3. [`data/benchmarking_results_with_result_stats.csv`](./data/benchmarking_results_with_result_stats.csv) contains (2) with additional statistics.
4. [`data/benchmarking_results_with_result_stats_agg.csv`](./data/benchmarking_results_with_result_stats_agg.csv) aggregates the data of (3).
5. [`data/dataset_stats.csv`](./data/dataset_stats.tsv) contains statistics about the datasets used in the evaluation.
6. [`data/index_sizes_and_loading_times.tsv`](./data/index_sizes_and_loading_times.tsv) contains statistics about building the indices with the different triple stores.
7. [`data/parsed_results_stats.csv`](./data/parsed_results_stats.csv) contains result counts for each query on each benchmark executed on each triple store.
8. [`data/result_stats_ground_truth.csv`](./data/result_stats_ground_truth.csv) contains expected result counts each query on each benchmark.
9. [`data/watdiv_query_names.tsv`](./data/watdiv_query_names.tsv) assigns each query from the WatDiv a name.  
10. [`output/figures`](./output/figures) contains the plots form the paper and for some plots additional tables with the data visualized in the corresponding plots.
11. [`raw_data`](./raw_data) this folder would contain the raw data before cleaning. Most of the data was omitted because it contains information that could uncover the authors.
12. [`raw_data/hypertrie_node_stats`](./raw_data/hypertrie_node_stats) this directory contains statistics on the hypertrie nodes used for storing the different datasets.

### Scripts

1. [`scripts/0_preprocess`](./scripts/0_preprocess) contains scripts to preprocess the data.
2. [`scripts`](./scripts) contains scripts starting with the prefix `paper-` which generate the plots in the paper.

