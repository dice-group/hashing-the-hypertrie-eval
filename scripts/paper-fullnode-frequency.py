from collections import defaultdict
from pathlib import Path

from plotnine import *

import pandas as pd
import numpy as np
from dfply import *
from plotnine.themes.themeable import strip_text
import matplotlib as mpl
import matplotlib.pyplot as plt
from util.human_format import human_format
from matplotlib import rc

# mpl.rcParams['image.cmap'] = 'Pastel2_r'
rc('text', usetex=True)
plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{lmodern,amsmath,amssymb,sansmathfonts}'

nodetype_mapping = {
    'baseline': 'b',
    'compression': 's',
    'hash': 'h',
    'hash+compression': 'hs',
    'hash+compression+inline': 'hsi'
}

dataset_mapping = {
    'dbpedia2015': "DBpedia",
    'swdf': "SWDF",
    'watdiv10000': "WatDiv",
    'WatDive': "WatDiv",
    'wikidata-2020-11-11': "Wikidata",
    'wikidata': "Wikidata",

}

light_color_map = defaultdict(lambda: "lightgrey")

color_map = defaultdict(lambda: "grey")
for colors in [light_color_map, color_map]:
    colors.update(**{
        'b': "#8DA0CB",
        # 's' : "#9F4A54",
        's': "#EFAAC4",
        'h': "#66C2A5",
        'hs': "#EDC707",
        'hsi': "#FC8D62"
    })

data_dir = Path("data")
raw_data_dir = Path("raw_data/hypertrie_node_stats")
if not data_dir.exists() or not raw_data_dir.exists():
    import sys

    print("There must be a data folder provided in the base-dir. "
          "By default the current working directory is used. ",
          file=sys.stderr)
    exit(1)

output_dir = Path("output/figures/")
output_dir.mkdir(parents=True, exist_ok=True)


class Dataset:
    def __init__(self, name, path):
        self.name = name
        self.path = Path(path)


swdf = Dataset("SWDF", raw_data_dir.joinpath("swdf"))
DBpedia = Dataset("DBpedia", raw_data_dir.joinpath("dbpedia2015"))
watdiv = Dataset("WatDive", raw_data_dir.joinpath("watdiv10000"))
wikidata = Dataset("wikidata", raw_data_dir.joinpath("wikidata-2020-11-11"))

long_node_counts = pd.DataFrame(columns=["hypertrie_type", "dataset", "depth", "node_type", "node_count"])

dataset = swdf
depth = 1

for dataset in [swdf, DBpedia, watdiv, wikidata]:
    for depth in [1, 2]:
        tsv_file = dataset.path.joinpath("depth_{depth}_node_count_comparison.tsv".format(depth=depth))
        tmp_data = pd.read_csv(tsv_file, sep='\t')

        tmp_data >>= (
                gather("node_type", "node_count", ["uncompressed_nodes", "compressed_nodes"])
                >> mutate(dataset=dataset.name,
                          depth=depth)
        )
        long_node_counts = long_node_counts.append(tmp_data)

long_node_counts["node_count"] = pd.to_numeric(long_node_counts["node_count"])

long_node_counts.replace(nodetype_mapping, inplace=True)
long_node_counts.replace(dataset_mapping, inplace=True)

# order hypertrie types
cat_order = ['b', 'h', 's', 'hs', 'hsi']
height_order = [2, 1]
dataset_order = ['SWDF', 'DBpedia', 'WatDiv', 'Wikidata']

long_fullnode_counts = pd.DataFrame(
    long_node_counts
        .query('node_type == "uncompressed_nodes"')
        .drop(columns=["depth", "node_type"])
        .groupby(['hypertrie_type', 'dataset'])
        .sum()
        .to_records())
long_fullnode_counts['hypertrie_type'] = pd.Categorical(long_fullnode_counts['hypertrie_type'], categories=cat_order,
                                                        ordered=True)
long_fullnode_counts['dataset'] = pd.Categorical(long_fullnode_counts['dataset'], categories=dataset_order,
                                                 ordered=True)

long_fullnode_counts.to_csv(str(data_dir.joinpath("long_fullnode_counts.tsv")), sep="\t", index=False)

large_font_size = 9
small_font_size = 6.5

# plot boxplot
p = (ggplot(data=long_fullnode_counts, mapping=aes(y='node_count', x='hypertrie_type', fill="hypertrie_type"))
     + geom_col()
     + scale_fill_manual(values=light_color_map)
     # + scale_fill_manual(values=["#b3cde3e0", "#8c96c6e0"])
     #   + stat_summary(shape='x', fun_data='mean_cl_normal')
     # + facet_grid(".~dataset", scales="free_y")
     + facet_wrap("dataset", scales="free_y", nrow=1)
     # + scale_y_continuous(labels=scientific_format(digits=2))
     + scale_y_continuous(labels=human_format())
     # + facet_grid("depth ~  dataset", scales="free", space = "free")
     + theme_light()
     + ylab('Full node count')
     + xlab('Hypertrie version')
     # + labs(fill='Node type')
     + theme(
            strip_background_x=element_text(color="#808080", ),
            subplots_adjust={'wspace': 0.4},
            axis_text_x=element_text(rotation=-90, hjust=0.5),
            axis_text_y=element_text(margin={"r": 0.8}),
            axis_title_x=element_text(size=large_font_size),
            axis_title_y=element_text(size=large_font_size),

            facet_spacing={"b": 1, "r": 50},
            # axis_text_x=element_blank(),
            # panel_grid_major=element_blank(),
            # panel_grid_minor=element_blank(),
            legend_position='none',
            # axis_ticks_major_x=element_blank(),
            # TODO: label nice machen
            # axis_text_y=element_text(weight="bold")
            figure_size=(5.5, .9),
            text=element_text(size=small_font_size)
        )
     )

name = "full-node-count"
p.save(str(output_dir.joinpath(f"paper-{name}.svg")))
save_as_pdf_pages([p], filename=output_dir.joinpath(f"paper-{name}.pdf").absolute(), bbox_inches="tight")
# print(p)
