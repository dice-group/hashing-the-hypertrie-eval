from collections import defaultdict

from plotnine import *
from dfply import *

from pathlib import Path

# TODO: nice colors

triplestore_mapping = {
    'blazegraph': 'Blazegraph',
    'fuseki': 'Fuseki',
    'fuseki-ltj': 'Fuseki-LTJ',
    'graphdb': 'graphDB',
    'gstore': 'gStore',
    'virtuoso': 'Virtuoso',
    'tentris-1.0.7_lsb_unused_0': 'Tentris-b',
    'tentris-1.1.0_lsb_unused_0': 'Tentris-hs',
    'tentris-1.1.0_lsb_unused_1': 'Tentris-hsi'
}
triplestore_order = [
    'Tentris-b',
    'Tentris-hs',
    'Tentris-hsi',
    'Blazegraph',
    'Fuseki',
    'Fuseki-LTJ',
    'graphDB',
    'gStore',
    'Virtuoso',
]
triplestore_order.reverse()

dataset_mapping = {
    'dbpedia2015': "DBpedia",
    'swdf': "SWDF",
    'watdiv10000': "WatDiv",
    'wikidata-2020-11-11': "Wikidata"
}

data_dir = Path("data")
if not data_dir.exists():
    import sys

    print("There must be a data folder provided in the base-dir. "
          "By default the current working directory is used. ",
          file=sys.stderr)
    exit(1)

output_dir = Path("output/figures/")
output_dir.mkdir(parents=True, exist_ok=True)

data: pd.DataFrame = pd.read_csv(data_dir.joinpath("index_sizes_and_loading_times.tsv").absolute(), sep="\t").dropna()
dataset_stats = pd.read_csv(data_dir.joinpath("dataset_stats.tsv").absolute(), sep="\t").dropna()

# to GB
data = data.merge(dataset_stats) >> mutate(
    bytes_per_statement=X.index_size / X.statements,
    statements1k_per_second=X.statements / 1000 / X.loading_time)

data["triplestore"] = data["triplestore"].replace(triplestore_mapping)
data["dataset"] = data["dataset"].replace(dataset_mapping)
# triplestore_order = data['triplestore'].value_counts().index.tolist()
data["triplestore"] = data["triplestore"].astype('category').cat.reorder_categories(triplestore_order)

# table entry strings
data["bytes_per_statement_label"] = data["bytes_per_statement"].apply(
    lambda x: "{:.0f}".format(x) if x > 1 else "{:.3f}".format(x))
data["statements1k_per_second_label"] = data["statements1k_per_second"].apply(
    lambda x: "{:.0f}".format(x) if x >= 10 else "{:.2f}".format(x))
# data["index_size_gb_label"] = data["index_size_gb"].apply(lambda x: "{:.0f}".format(x) if x > 1 else "{:.3f}".format(x))
# data["loading_time_label"] = data["loading_time"].apply(lambda x: "{:.0f}".format(x) if x >= 10 else "{:.2f}".format(x))
#
data >>= (
        group_by(X.dataset)
        >> mutate(max_bytes_per_statement=colmax(X.bytes_per_statement),
                  max_statements1k_per_second=colmax(X.statements1k_per_second))
        >> ungroup()
        >> mutate(index_size_y_pad=X.max_bytes_per_statement * 0.05,
                  loading_time_y_pad=X.max_statements1k_per_second * 0.05)
)


def index_stats_plot(name: str,
                     data: pd.DataFrame,
                     x: str, y: str, color_map: dict, data_labels: str, padding: str, ylabel: str) -> ggplot:
    p = (ggplot(data=data) +
         geom_bar(aes(y=y, x=x, fill=x), stat="identity", position='dodge')
         + scale_fill_manual(values=color_map)
         + geom_text(aes(label=data_labels, x=x, y=padding), va='center', ha='left')
         + facet_grid(".~dataset", scales="free_x")
         + ylab(ylabel)
         + xlab("")
         + ylim(0.0, data[y].max() * 1.01)
         + coord_flip()
         + theme_light()
         + theme(
                # strip_background=element_rect(fill="steelblue"),
                axis_text_x=element_blank(),
                panel_grid_major=element_blank(),
                panel_grid_minor=element_blank(),
                legend_position='none',
                # axis_text_y=element_text(weight="bold")
            )
         )
    save_as_pdf_pages([p], filename=output_dir.joinpath(f"paper-{name}.pdf").absolute())
    p.save(output_dir.joinpath(f"paper-{name}.svg").absolute())
    return p


color_map = defaultdict(lambda: "lightgrey")
color_map.update(**{
    'Tentris-b': "#8da0cb",
    'Tentris-hs': "#66c2a5",
    'Tentris-hsi': "#fc8d62"
})
index_stats_plot(name="index-sizes",
                 data=data,
                 x='triplestore',
                 y='bytes_per_statement',
                 color_map=color_map,
                 data_labels='bytes_per_statement_label',
                 padding='index_size_y_pad',
                 ylabel="Index size in bytes per statement")

index_stats_plot(name="loading-times",
                 data=data,
                 x='triplestore',
                 y='statements1k_per_second',
                 color_map=color_map,
                 data_labels='statements1k_per_second_label',
                 padding='loading_time_y_pad',
                 ylabel="Loading speed in 1k statements per second")
