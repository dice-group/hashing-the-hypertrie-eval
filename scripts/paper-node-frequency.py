from collections import defaultdict
from pathlib import Path

from plotnine import *

import pandas as pd
import numpy as np
from dfply import *
from plotnine.themes.themeable import strip_text
import matplotlib as mpl

from util.human_format import human_format

mpl.rcParams['image.cmap'] = 'Pastel2_r'
mpl.rcParams.update({'font.sans-serif':'Linux Biolinum O'})
mpl.rcParams.update({'font.family':'serif'})

subscript_map = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆",
    "7": "₇", "8": "₈", "9": "₉", "a": "ₐ", "b": "♭", "c": "꜀", "d": "ᑯ",
    "e": "ₑ", "f": "բ", "g": "₉", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
    "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "q": "૧", "r": "ᵣ",
    "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "w": "w", "x": "ₓ", "y": "ᵧ",
    "z": "₂", "A": "ₐ", "B": "₈", "C": "C", "D": "D", "E": "ₑ", "F": "բ",
    "G": "G", "H": "ₕ", "I": "ᵢ", "J": "ⱼ", "K": "ₖ", "L": "ₗ", "M": "ₘ",
    "N": "ₙ", "O": "ₒ", "P": "ₚ", "Q": "Q", "R": "ᵣ", "S": "ₛ", "T": "ₜ",
    "U": "ᵤ", "V": "ᵥ", "W": "w", "X": "ₓ", "Y": "ᵧ", "Z": "Z", "+": "₊",
    "-": "₋", "=": "₌", "(": "₍", ")": "₎"}

sub_trans = str.maketrans(
    ''.join(subscript_map.keys()),
    ''.join(subscript_map.values()))

superscript_map = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶",
    "7": "⁷", "8": "⁸", "9": "⁹", "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ",
    "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ᶦ", "j": "ʲ", "k": "ᵏ",
    "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "۹", "r": "ʳ",
    "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ",
    "z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ᶜ", "D": "ᴰ", "E": "ᴱ", "F": "ᶠ",
    "G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ",
    "N": "ᴺ", "O": "ᴼ", "P": "ᴾ", "Q": "Q", "R": "ᴿ", "S": "ˢ", "T": "ᵀ",
    "U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "X": "ˣ", "Y": "ʸ", "Z": "ᶻ", "+": "⁺",
    "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾"}

trans = str.maketrans(
    ''.join(superscript_map.keys()),
    ''.join(superscript_map.values()))

# TODO: sort-order
# TODO: nice colors

triplestore_mapping = {
    'blazegraph': 'Blazegraph',
    'fuseki': 'Fuseki',
    'graphdb': 'graphDB',
    'gstore': 'gStore',
    'virtuoso': 'Virtuoso',
    'tentris-1.0.7_lsb_unused_0': 'Tentris-b',
    'tentris-1.1.0_lsb_unused_0': 'Tentris-hs',
    'tentris-1.1.0_lsb_unused_1': 'Tentris-hsi'
}

triplestore_short_mapping = {
    'blazegraph': 'B',
    'fuseki': 'F',
    'graphdb': 'G',
    'gstore': 'S',
    'virtuoso': 'V',
    'tentris-1.0.7': 'Tb',
    'tentris-1.0.7_lsb_unused_0': 'Tb',
    'tentris-1.1.0_lsb_unused_0': 'Th',
    'tentris-1.1.0-lsb_unused_0': 'Th',
    'tentris-1.1.0_lsb_unused_1': 'Ti',
    'tentris-1.1.0-lsb_unused_1': 'Ti',
}

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
        'Tb': "#EB6F82",  # Dark Salmon Pink
        'Th': "#d9bb45",  # Dark Medium Champagne
        'Ti': "#49ABAB"  # Dark Maximum Blue Green
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
cat_order = ['b', 's', 'h', 'hs', 'hsi']
long_node_counts['hypertrie_type'] = pd.Categorical(long_node_counts['hypertrie_type'], categories=cat_order,
                                                    ordered=True)
height_order = [2, 1]
long_node_counts['Height'] = pd.Categorical(long_node_counts['depth'], categories=height_order, ordered=True)
dataset_order = ['SWDF', 'DBpedia', 'WatDiv', 'Wikidata']
long_node_counts['Dataset'] = pd.Categorical(long_node_counts['dataset'], categories=dataset_order, ordered=True)

long_node_counts.to_csv(str(data_dir.joinpath("long_node_counts.tsv")), sep="\t", index=False)

# plot boxplot
p = (ggplot(data=long_node_counts, mapping=aes(y='node_count', x='hypertrie_type', fill="node_type"))
     + geom_col()
     + scale_fill_manual(values=["#b3cde3e0","#8c96c6e0"])
     #   + stat_summary(shape='x', fun_data='mean_cl_normal')
     + facet_wrap("~ Height + Dataset", scales="free_y", nrow=2, labeller='label_both')
     # + scale_y_continuous(labels=scientific_format(digits=2))
     + scale_y_continuous(labels=human_format())
     # + facet_grid("depth ~  dataset", scales="free", space = "free")
     + theme_light()
     + ylab('Node count')
     + xlab('')
     + labs(fill='Node type')
     + theme(subplots_adjust={'wspace': 0.4},
             axis_text_x=element_text(rotation=90, hjust=0.5),
             # axis_text_x=element_blank(),
             # panel_grid_major=element_blank(),
             # panel_grid_minor=element_blank(),
             legend_position='none',
             # axis_ticks_major_x=element_blank(),
             # TODO: label nice machen
             # axis_text_y=element_text(weight="bold")
             figure_size=(7.5, 3),
            text=element_text(family="Linux Biolinum O", size=9)
             )
     )

name = "paper-node-count"
p.save(str(output_dir.joinpath(f"{name}.svg")))
p.save(str(output_dir.joinpath(f"{name}.pdf")))
# print(p)
