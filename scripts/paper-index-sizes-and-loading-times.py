from collections import defaultdict

import pandas as pd
from matplotlib.texmanager import TexManager
from plotnine import *
from dfply import *

from pathlib import Path

import matplotlib as mpl

import matplotlib.pyplot as plt
from matplotlib import rc

triplestore_mapping = {
    'blazegraph': 'B',
    'fuseki': 'F',
    'fuseki-ltj': 'Fl',
    'graphdb': 'G',
    'gstore': 'S',
    'virtuoso': 'V',
    'tentris-1.0.7_lsb_unused_0': 'T-b',
    'tentris-1.1.0_hashing_only': 'T-h',
    'tentris-1.1.0_lsb_unused_0': 'T-hs',
    'tentris-1.1.0_lsb_unused_1': 'T-hsi',
}
triplestore_order = [
    'T-b',
    'T-h',
    'T-hs',
    'T-hsi',
    'B',
    'F',
    'Fl',
    'G',
    'S',
    'V',
]
triplestore_order.reverse()

dataset_mapping = {
    'dbpedia2015': "DBpedia",
    'swdf': "SWDF",
    'watdiv10000': "WatDiv",
    'wikidata-2020-11-11': "Wikidata"
}

datasets = ['SWDF', 'DBpedia', 'WatDiv', 'Wikidata']

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
print(data["triplestore"].unique())

# table entry strings
data["bytes_per_statement_label"] = data["bytes_per_statement"].apply(
    lambda x: "{:.0f}".format(x) if x > 1 else "{:.3f}".format(x))
data["statements1k_per_second_label"] = data["statements1k_per_second"].apply(
    lambda x: "{:.0f}".format(x) if x >= 10 else "{:.2f}".format(x))

data >>= (
        group_by(X.dataset)
        >> mutate(max_bytes_per_statement=colmax(X.bytes_per_statement),
                  max_statements1k_per_second=colmax(X.statements1k_per_second))
        >> ungroup()
        >> mutate(index_size_y_pad=X.max_bytes_per_statement * 0.05,
                  loading_time_y_pad=X.max_statements1k_per_second * 0.05)
)

na_text = pd.DataFrame(data={
    'triplestore': ["T-b", "S"], 'dataset': 2 * ['Wikidata']}
)
na_text['dataset'] = pd.Categorical(na_text['dataset'], categories=datasets, ordered=True)
na_text['triplestore'] = pd.Categorical(na_text['triplestore'], categories=triplestore_order, ordered=True)


def index_stats_plot(name: str,
                     data: pd.DataFrame,
                     x: str, y: str,
                     color_map: dict,
                     data_labels: str,
                     padding: str,
                     ylabel: str,
                     title: str,
                     with_x_legend: bool,
                     na_text: pd.DataFrame) -> ggplot:
    rc('text', usetex=True)
    plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.preamble'] = r'\usepackage{lmodern,amsmath,amssymb,sansmathfonts}'
    large_font_size = 9
    small_font_size = 7
    p = (ggplot(data=data) +
         geom_bar(aes(y=y, x=x, fill=x), stat="identity", position='dodge')
         + scale_fill_manual(values=color_map)
         + geom_text(aes(label=data_labels, x=x, y=padding), va='center', ha='left', size=small_font_size)
         + geom_text(data=na_text, mapping=aes(x=x, y=0), va='center', ha='left', label="n\!/\!a", color="grey", size=small_font_size, )
         + facet_grid(".~dataset", scales="free_x")
         + ylab(ylabel)
         + xlab("Triple store" if with_x_legend else "")
         + ylim(0.0, data[y].max() * 1.01)
         + coord_flip()
         + theme_light()
       #  + ggtitle(title)
         + theme(
                strip_background_x=element_text(color="#808080"),
                axis_text_x=element_blank(),
                axis_title_x=element_text(margin={'t': 6, 'b': 0}, size=large_font_size),
                axis_title_y=element_text(size=large_font_size),
                #title=element_text(size=large_font_size),
                panel_grid_major=element_blank(),
                panel_grid_minor=element_blank(),
                panel_spacing=.03,
                axis_text_y=None if with_x_legend else element_blank(),
                axis_ticks_major_y=None if with_x_legend else element_blank(),
                axis_ticks_major_x=element_blank(),
                legend_position='none',
                figure_size=(2.5, 2.1),
                text=element_text(size=small_font_size) #family="Latin Modern Sans",
            )
         )
    save_as_pdf_pages([p], filename=output_dir.joinpath(f"paper-{name}.pdf").absolute(), bbox_inches="tight")
    p.save(output_dir.joinpath(f"paper-{name}.svg").absolute())
    return p


color_map = defaultdict(lambda: "lightgrey")
color_map.update(**{
    'T-b': "#8DA0CB",
    'T-h': "#66C2A5",
    'T-hs': "#EDC707",
    'T-hsi': "#FC8D62"
})

dataset_order = ['SWDF', 'DBpedia', 'WatDiv', 'Wikidata']
data['dataset'] = pd.Categorical(data['dataset'], categories=dataset_order, ordered=True)

index_stats_plot(name="index-sizes",
                 data=data,
                 x='triplestore',
                 y='bytes_per_statement',
                 color_map=color_map,
                 data_labels='bytes_per_statement_label',
                 padding='index_size_y_pad',
                 ylabel=r"bytes/triple ($\blacktriangleleft$ less is better)",
                 title="Storage Efficiency",
                 with_x_legend=True,
                 na_text=na_text
                 )

index_stats_plot(name="loading-times",
                 data=data,
                 x='triplestore',
                 y='statements1k_per_second',
                 color_map=color_map,
                 data_labels='statements1k_per_second_label',
                 padding='loading_time_y_pad',
                 ylabel=r"1k triple/second ($\blacktriangleright$ more is better)", #$\blacktriangleleft$
                 title="Loading Speed",
                 with_x_legend=False,
                 na_text=na_text
                 )
