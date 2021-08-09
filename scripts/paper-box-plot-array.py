# TODO: sort-order
# TODO: nice colors

import pathlib
from collections import defaultdict

from plotnine import *

import pandas as pd
import numpy as np
from dfply import *
from plotnine.themes.themeable import strip_text
import matplotlib as mpl

mpl.rcParams['image.cmap'] = 'Pastel2_r'

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

triplestore_mapping = {
    'blazegraph': 'Blazegraph',
    'fuseki': 'Fuseki',
    'graphdb': 'graphDB',
    'gstore': 'gStore',
    'virtuoso': 'Virtuoso',
    'tentris-1.0.7_lsb_unused_0': 'Tentris basline',
    'tentris-1.1.0_lsb_unused_0': 'Tentris hash+sen',
    'tentris-1.1.0_lsb_unused_1': 'Tentris hash+sen+inline'
}

triplestore_short_mapping = {
    'blazegraph': 'B',
    'fuseki': 'F',
    'fuseki-ltj': 'Fl',
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
dataset_mapping = {
    'dbpedia2015': "DBpedia",
    'swdf': "SWDF",
    'watdiv10000': "WatDiv",
    'wikidata-2020-11-11': "Wikidata"
}

light_color_map = defaultdict(lambda: "lightgrey")

color_map = defaultdict(lambda: "grey")
for colors in [light_color_map, color_map]:
    colors.update(**{
        'Tb': "#8da0cb",
        'Th': "#66c2a5",
        'Ti': "#fc8d62"
    })

# check if the right dir is used
data_dir = pathlib.Path("data")
if not data_dir.exists():
    import sys

    print("There must be a data folder provided in the base-dir. "
          "By default the current working directory is used. ",
          file=sys.stderr)
    exit(1)

output_dir = "output/figures/"
pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

iguana_data = pd.read_csv("data/benchmarking_results_with_result_stats.csv")  # .fillna(np.nan).convert_dtypes()

iguana_data_agg = pd.read_csv("data/benchmarking_results_with_result_stats_agg.csv")  # .fillna(np.nan).convert_dtypes()

for dataset in [iguana_data, iguana_data_agg]:
    dataset.replace(triplestore_short_mapping, inplace=True)
    dataset.replace(dataset_mapping, inplace=True)

# iguana_data = iguana_data.query("triplestore != 'Tb' and triplestore != 'Th'")
# iguana_data_agg = iguana_data_agg.query("triplestore != 'Tb' and triplestore != 'Th'")

iguana_data_agg['runtime'] = 1 / iguana_data_agg['qps_mean']

cat_order = [
    'Tb',
    'Th',
    'Ti',
    'B',
    'F',
    'Fl',
    'G',
    'S',
    'V',
]
dataset['triplestore'] = pd.Categorical(dataset['triplestore'], categories=cat_order,
                                        ordered=True)
iguana_data_agg['triplestore'] = pd.Categorical(iguana_data_agg['triplestore'], categories=cat_order,
                                                ordered=True)

data_agg = (iguana_data_agg >> group_by('dataset', 'triplestore')
            >> summarize(mean_qps=np.mean(X.qps_mean),
                         mean_runtime=np.mean(X.runtime))
            >> mutate(avgQpS_rounded=np.round(X.mean_qps).astype(int))
            )
ticks = [10 ** i for i in range(-4, 5)]
tick_labels = ["10{}".format(str(i).translate(trans)) for i in range(-4, 5)]

# from matplotlib import rc
# rc('text', usetex=True)
# tick_labels = ["$10^{i}$" for i in range(-3,5)]

# plot boxplot
p = (ggplot(data=iguana_data_agg, mapping=aes(y='qps_mean', x='triplestore'))
     + geom_jitter(alpha=0.3, mapping=aes(fill='triplestore', color='triplestore'),
                   na_rm=True,
                   stroke=0)
     + geom_boxplot(outlier_stroke=0, outlier_alpha=0.8, outlier_size=0.8, alpha=0, fatten=1)
     + scale_y_log10(breaks=ticks,
                     labels=tick_labels)
     + scale_fill_manual(values=color_map)

     #   + stat_summary(shape='x', fun_data='mean_cl_normal')
     + facet_grid(".~dataset", scales="free_y")
     + theme_light()
     + ylab('Average QpS')
     + xlab('')
     + geom_point(data=data_agg, mapping=aes(x='triplestore', y='mean_qps'), shape='x')
     + theme(
            axis_text_x=element_blank(),
            # panel_grid_major=element_blank(),
            # panel_grid_minor=element_blank(),
            legend_position='none',
            axis_ticks_major_x=element_blank(),
            # TODO: label nice machen
            # axis_text_y=element_text(weight="bold")
            figure_size=(7.5, 2)
        )
     )
name = "paper-box-plot"

# print(p)

fully_agg = (iguana_data >> group_by("triplestore", "dataset")
             >> summarize(QMpH=1 * 60 ** 2 * 1000 / np.sum(X.penalizedTime) * np.max(X.run) + 1,
                          sum_succeeded=np.sum(X.succeeded),
                          sum_failed=np.sum(X.failed))
             >> mutate(QMpH_rounded=np.round(X.QMpH).astype(int))
             )

fully_agg['triplestore'] = pd.Categorical(fully_agg['triplestore'], categories=cat_order,
                                          ordered=True)

# data_agg.merge(fully_agg, on=["triplestore", "dataset"]).to_csv("iguana_data_fully_agg.tsv", sep="\t")

tick_labels = ["  10{}".format(str(i).translate(trans)) for i in range(-4, 5)]

q = (ggplot(data=fully_agg, mapping=aes(y='QMpH', x='triplestore', fill="triplestore"))
     + geom_bar(stat="identity", position='dodge', alpha=0.85)
     + scale_y_log10(breaks=ticks,
                     labels=tick_labels,
                     # expand=(0, 0, 0.3, 0)
                     )
     + scale_fill_manual(values=light_color_map)
     + facet_grid(".~dataset", scales="free_y")
     + xlab("Triplestore")
     # + geom_text(mapping=aes(label='QMpH_rounded'), size=5, va='bottom', angle="45" )
     + theme_light()
     + theme(strip_background=element_blank(),
             strip_text=element_blank(),
             # panel_grid_major=element_blank(),
             # panel_grid_minor=element_blank(),
             legend_position='none',
             # axis_text_y=element_text(weight="bold")
             figure_size=(7.5, 1)
             )
     )
# print(q)
name = "paper-benchmark-results"
save_as_pdf_pages([p, q], filename=f"{output_dir}{name}.pdf", bbox_inches="tight", pad_inches=0.03)
p.save(f"{output_dir}{name}-scatter.svg")
q.save(f"{output_dir}{name}-QMpH.svg")

iguana_data_agg.to_csv(f"{output_dir}{name}-scatter.tsv", sep="\t", index=None)
fully_agg.to_csv(f"{output_dir}{name}-QMpH.tsv", sep="\t", index=None)

# q.save(f"{output_dir}{name}.svg")
# print(q)

# from matplotlib import gridspec
# fig = (ggplot()+geom_blank(data=fully_agg)+theme_void()).draw()
#
# gs = gridspec.GridSpec(1,2)
# ax1 = fig.add_subplot(gs[0,0])
# ax2 = fig.add_subplot(gs[0,1])
#
#
# # Add subplots to the figure
# _ = p._draw_using_figure(fig, [ax1])
# _ = q._draw_using_figure(fig, [ax2])
# fig.show()
# fig.save("xxxxxxxxxxx.svg")


# q = (ggplot(data=iguana_data_agg, mapping=aes(y='runtime', x='triplestore'))
#      + geom_jitter(alpha=0.1, mapping=aes(fill='triplestore', color='triplestore'))
#      + geom_boxplot(outlier_alpha=0.8, outlier_size=0.8, alpha=0)
#      # + scale_y_log10()
#      # + stat_summary(shape = 'x')
#      + facet_grid(".~dataset", scales="free_y")
#      + theme_light()
#      + ylab('Average runtime')
#      + geom_point(data=data_agg, mapping=aes(x='triplestore', y='mean_runtime'), shape='x', color='#DB57B2')
#      + theme(strip_background=element_rect(fill="steelblue"),
#              # axis_text_x=element_blank(),
#              panel_grid_major=element_blank(),
#              panel_grid_minor=element_blank(),
#              legend_position='none',
#              # axis_text_y=element_text(weight="bold")
#              )
#      )
# print(q)


watdiv_iguana_data_agg = iguana_data_agg.query("dataset == 'WatDiv'")
triplestore = 'Ti'
tmp = watdiv_iguana_data_agg.query(f"triplestore == '{triplestore}'")


def func(d: pd.DataFrame):
    norm = tmp.query(f"queryID == {d.queryID}").qps_mean

    if norm.empty:
        return None

    value = d.qps_mean
    # if (d.triplestore == "gstore"):
    #     print(f"queryID {d.queryID}")
    #     print(f"triplestore {d.triplestore}")
    #     print(norm)
    #     print(value)
    if value:
        normed_value = np.float64(value) / np.float64(norm)
        # if (d.triplestore == "gstore"):
        #     print(normed_value)
        return normed_value
    else:
        return None


watdiv_iguana_data_agg[f'avgQPS relative to {triplestore}'] = watdiv_iguana_data_agg.apply(func, axis=1).values
watdiv_iguana_data_agg[f'QpS rel. to {triplestore}'] = np.log10(
    watdiv_iguana_data_agg[f'avgQPS relative to {triplestore}'])

watdiv_iguana_data_agg['triplestore'] = pd.Categorical(watdiv_iguana_data_agg['triplestore'],
                                                       categories=list(reversed(cat_order)),
                                                       ordered=True)

r = (ggplot(watdiv_iguana_data_agg, aes('queryID', 'triplestore', fill=f'QpS rel. to {triplestore}'))
     + geom_tile()
     # + geom_text(aes(label=f'avgQPS relative to {triplestore}'), size=10)
     + xlab("Query ID")
     + ylab("Triplestore")
     # + geom_text(mapping=aes(label='QMpH_rounded'), size=5, va='bottom', angle="45" )
     + theme_light()
     + theme(strip_background=element_blank(),
             strip_text=element_blank(),
             panel_grid_major=element_blank(),
             panel_grid_minor=element_blank(),
             # legend_text=element_text('speedup (log10)'),
             # legend_position='none',
             # axis_text_y=element_text(weight="bold")
             figure_size=(6.5, 1.25),
             legend_title_align='center',
             )
     + scale_fill_gradient2(low="#08519c", mid="#f7fbff", high="red",  # colors in the scale
                            midpoint=0,  # same midpoint for plots (mean of the range)
                            breaks=list(range(-4, 2)),  # breaks in the scale bar
                            labels=["10" + str(x).translate(trans) if x != 0 else "1" for x in range(-4, 2)],
                            limits=(1, -4.5),
                            na_value="black"
                            )
     )
name = "paper-heatmap-watdiv-rel-T-hsi"
save_as_pdf_pages([r], filename=f"{output_dir}{name}.pdf", bbox_inches="tight")
watdiv_iguana_data_agg.to_csv(f"{output_dir}{name}.tsv", sep="\t", index=None)
r.save(f"{output_dir}{name}.svg")
# print(q)
