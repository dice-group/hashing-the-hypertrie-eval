import pathlib
from collections import defaultdict
from typing import List

from plotnine import *

import pandas as pd
import numpy as np
from dfply import *
from plotnine.themes.themeable import strip_text
import matplotlib as mpl

import matplotlib.pyplot as plt
from matplotlib import rc

rc('text', usetex=True)
plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{lmodern,amsmath,amssymb,sansmathfonts}'
# plt.rcParams.update({
#     "pgf.texsystem": "pdflatex"})

mpl.rcParams['image.cmap'] = 'Pastel2_r'

triplestore_mapping = {
    'blazegraph': 'Blazegraph',
    'fuseki': 'Fuseki',
    'graphdb': 'graphDB',
    'gstore': 'gStore',
    'virtuoso': 'Virtuoso',
    'tentris-1.0.7_lsb_unused_0': 'Tentris basline',
    'tentris-1.1.0_hashing_only': 'Tentris hash',
    'tentris-1.1.0-hashing_only': 'Tentris hash',
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
    'tentris-1.0.7': 'T-b',
    # 'tentris-1.0.7_lsb_unused_0': 'T-b',
    'tentris-1.1.0_lsb_unused_0': 'T-hs',
    'tentris-1.1.0-lsb_unused_0': 'T-hs',
    'tentris-1.1.0_hashing_only': 'T-h',
    'tentris-1.1.0-hashing_only': 'T-h',
    'tentris-1.1.0_lsb_unused_1': 'T-hsi',
    'tentris-1.1.0-lsb_unused_1': 'T-hsi',
}

large_font_size = 9
small_font_size = 7
tiny_font_size = 4.5

dataset_mapping = {
    'dbpedia2015': "DBpedia",
    'swdf': "SWDF",
    'watdiv10000': "WatDiv",
    'wikidata-2020-11-11': "Wikidata"
}


def minor_log10_breaks(min: float, max: float) -> List[float]:
    import math
    min_exp = math.floor(math.log10(min))
    max_exp = math.ceil(math.log10(max))
    breaks = [10 ** t * i for t in range(min_exp, max_exp + 1) for i in range(2, 10)]
    breaks = [n for n in breaks if n >= min and n <= max]
    return breaks


light_color_map = defaultdict(lambda: "lightgrey")

color_map = defaultdict(lambda: "grey")
for colors in [light_color_map, color_map]:
    colors.update(**{
        'T-b': "#8DA0CB",
        'T-h': "#66C2A5",
        'T-hs': "#EDC707",
        'T-hsi': "#FC8D62"
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

# iguana_data = iguana_data.query("triplestore != 'T-b' and triplestore != 'Th'")
# iguana_data_agg = iguana_data_agg.query("triplestore != 'T-b' and triplestore != 'Th'")

iguana_data_agg['runtime'] = 1 / iguana_data_agg['qps_mean']

triplestores = [
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
for dataset in [iguana_data, iguana_data_agg]:
    dataset.replace(triplestore_short_mapping, inplace=True)
    dataset.replace(dataset_mapping, inplace=True)
    dataset['triplestore'] = pd.Categorical(dataset['triplestore'], categories=triplestores,
                                            ordered=True)

data_agg = (iguana_data_agg >> group_by('dataset', 'triplestore')
            >> summarize(mean_qps=np.mean(X.qps_mean),
                         mean_runtime=np.mean(X.runtime))
            >> mutate(avgQpS_rounded=np.round(X.mean_qps).astype(int))
            )
ticks = [10 ** i for i in range(-4, 5)]
tick_labels = ["$10^{{{} }}$".format(i) if i != 0 else "1" for i in range(-4, 5)]

datasets = ['SWDF', 'DBpedia', 'WatDiv', 'Wikidata']
data_agg['dataset'] = pd.Categorical(data_agg['dataset'], categories=datasets, ordered=True)
iguana_data_agg['dataset'] = pd.Categorical(iguana_data_agg['dataset'], categories=datasets, ordered=True)

# from matplotlib import rc
# rc('text', usetex=True)
# tick_labels = ["$10^{i}$" for i in range(-3,5)]


timeout_text = pd.DataFrame(data={
    'triplestore': [1], 'mean_qps': [1 / 120], 'dataset': 'SWDF', 'label': 'timeout'}
)
timeout_text['dataset'] = pd.Categorical(timeout_text['dataset'], categories=datasets, ordered=True)

na_text = pd.DataFrame(data={
    'triplestore': ["T-b", "S"], 'mean_qps': 2 * [1 / 73], 'dataset': 2 * ['Wikidata'], }
)
na_text['dataset'] = pd.Categorical(na_text['dataset'], categories=datasets, ordered=True)
na_text['triplestore'] = pd.Categorical(na_text['triplestore'], categories=triplestores, ordered=True)

# plot boxplot
p = (ggplot(data=iguana_data_agg.query("qps_mean > 1/180 and not wrongResult"),
            mapping=aes(y='qps_mean', x='triplestore'))
     + geom_jitter(alpha=0.4, mapping=aes(fill='triplestore', color='triplestore'),
                   na_rm=True,
                   size=.9,
                   stroke=0)
     + geom_boxplot(outlier_stroke=0, outlier_alpha=0.8, outlier_size=0.8, alpha=0, fatten=1, size=.4)
     + scale_y_log10(breaks=ticks,
                     labels=tick_labels,
                     minor_breaks=minor_log10_breaks(1 / 180, 10 ** 4),
                     )
     + scale_fill_manual(values=color_map)

     # + stat_summary(shape='x', fun_data='mean_cl_normal')
     + facet_grid(".~dataset", scales="free_y")
     + theme_light()
     + ylab('QpS')
     + xlab('')
     + geom_point(data=data_agg, mapping=aes(x='triplestore', y='mean_qps'), shape='x')
     + geom_text(data=timeout_text, mapping=aes(x='triplestore', y='mean_qps', label="label"), color="red",
                 size=tiny_font_size,
                 nudge_x=0.66,
                 nudge_y=.1,
                 alpha=.7,
                 )
     + geom_text(data=na_text, mapping=aes(x='triplestore', y='mean_qps'), label="n\!/\!a", color="grey",
                 size=tiny_font_size)
     + geom_hline(yintercept=0.0055, color="#FF000099", alpha=.7)
     + theme(
            strip_background_x=element_text(color="#808080", ),
            axis_text_x=element_blank(),
            # panel_grid_major=element_blank(),
            # panel_grid_minor=element_blank(),
            axis_title_x=element_text(size=large_font_size),
            legend_position='none',
            axis_ticks_major_x=element_blank(),
            # TODO: label nice machen
            # axis_text_y=element_text(weight="bold")
            figure_size=(5.5, 1.2),
            text=element_text(family="Latin Modern Sans", size=small_font_size)
        )
     )
print(p)  ## Problem tritt hier auf
name = "paper-box-plot"

fully_agg = (iguana_data >> group_by("triplestore", "dataset")
             >> summarize(QMpH=1 * 60 ** 2 * 1000 / np.sum(X.penalizedTime) * np.max(X.run) + 1,
                          sum_succeeded=np.sum(X.succeeded),
                          sum_failed=np.sum(X.failed))
             >> mutate(QMpH_rounded=X.QMpH.apply(
            lambda x: format(x, '.2f') if x < 10 else format(x, '.1f') if x < 100 else format(x, '.0f')))
             )

fully_agg['triplestore'] = pd.Categorical(fully_agg['triplestore'], categories=triplestores,
                                          ordered=True)
datasets = ['SWDF', 'DBpedia', 'WatDiv', 'Wikidata']
fully_agg['dataset'] = pd.Categorical(fully_agg['dataset'], categories=datasets, ordered=True)

# data_agg.merge(fully_agg, on=["triplestore", "dataset"]).to_csv("iguana_data_fully_agg.tsv", sep="\t")

ticks = [10 ** i for i in range(0, 4)]
tick_labels = ["$10^{{{} }}$".format(i) if i != 0 else "1" for i in range(0, 4)]
# tick_labels = ["\makebox[2cm]{{x\hfill$10^{{{} }}$}}".format(i) if i != 0 else "1" for i in range(0, 4)]
#         
na_text = pd.DataFrame(data={
    'triplestore': ["T-b", "S"], 'mean_qps': 2 * [1.5], 'dataset': 2 * ['Wikidata'], }
)
na_text['dataset'] = pd.Categorical(na_text['dataset'], categories=datasets, ordered=True)
na_text['triplestore'] = pd.Categorical(na_text['triplestore'], categories=triplestores, ordered=True)

q = (ggplot(data=fully_agg, mapping=aes(y='QMpH', x='triplestore', fill="triplestore"))
     + geom_bar(stat="identity", position='dodge', alpha=0.85)
     + scale_y_log10(breaks=ticks,
                     labels=tick_labels,
                     expand=(0, 0.23, 0.3, 0),
                     minor_breaks=minor_log10_breaks(1, 2000)
                     )
     + scale_fill_manual(values=light_color_map)
     + facet_grid(".~dataset", scales="free_y")
     + geom_text(mapping=aes(label='QMpH_rounded'), size=tiny_font_size, va='bottom', angle="45", color="#4D4D4D")
     + geom_text(data=na_text, mapping=aes(x='triplestore', y='mean_qps'), label="n\!/\!a", color="grey",
                 size=tiny_font_size, )
     + xlab('')
     + theme_light()
     + theme(
            axis_title_y=element_text(margin={"r": 7.48}, size=large_font_size),
            strip_background=element_blank(),
            strip_text=element_blank(),
            # panel_grid_major=element_blank(),
            # panel_grid_minor=element_blank(),
            legend_position='none',
            axis_ticks_major_x=element_blank(),
            axis_text_x=element_blank(),
            # axis_text_y=element_text(weight="bold")
            figure_size=(5.5, 1),
            text=element_text(family="Latin Modern Sans", size=small_font_size)
        )
     )

ticks = [x * 10 for x in range(0, 10)]
tick_labels = [f"${i}$" for i in ticks]
#          
# ticks = [float(x) for x in ticks]

na_text = pd.DataFrame(data={
    'triplestore': ["T-b", "S"], 'mean_qps': 2 * [1.2], 'dataset': 2 * ['Wikidata'], }
)
na_text['dataset'] = pd.Categorical(na_text['dataset'], categories=datasets, ordered=True)
na_text['triplestore'] = pd.Categorical(na_text['triplestore'], categories=triplestores, ordered=True)

fully_agg >>= mutate(percent_failed=100 * X.sum_failed / (X.sum_succeeded + X.sum_failed))
r = (ggplot(data=fully_agg, mapping=aes(y='percent_failed', x='triplestore', fill="triplestore"))
     + geom_bar(stat="identity", position='dodge', alpha=0.85)
     + scale_fill_manual(values=light_color_map)
     + facet_grid(".~dataset", scales="free_y")
     + xlab("Triple store")
     + scale_y_continuous(breaks=ticks, labels=tick_labels,
                          limits=(0, fully_agg.percent_failed.max() * 1.15),
                          name="$\%$ failed Q")
     + geom_text(data=fully_agg.query("sum_failed > 0"),
                 mapping=aes(label='percent_failed'),
                 # stat='percent_failed',
                 size=tiny_font_size,
                 va='bottom',
                 # nudge_x=.1,
                 # format_string='{:.0f}% ',
                 format_string='{:.0f}',
                 color="#4D4D4D",
                 )
     + geom_text(data=na_text, mapping=aes(x='triplestore', y='mean_qps'), label="n\!/\!a", color="grey",
                 size=tiny_font_size, nudge_y=.7, )
     + theme_light()
     + theme(strip_background=element_blank(),
             axis_title_y=element_text(margin={"r": 10.13}, size=large_font_size),
             axis_title_x=element_text(size=large_font_size),
             strip_text=element_blank(),
             # panel_grid_major=element_blank(),
             # panel_grid_minor=element_blank(),
             legend_position='none',
             # axis_text_y=element_text(weight="bold")
             axis_text_x=element_text(rotation=-90, hjust=0.5),
             figure_size=(5.5, .75),
             text=element_text(family="Latin Modern Sans", size=small_font_size)
             )

     )

# print(q)
name = "paper-benchmark-results"
save_as_pdf_pages([p, q, r], filename=f"{output_dir}{name}.pdf", bbox_inches="tight", pad_inches=0.03)
p.save(f"{output_dir}{name}-scatter.svg")
q.save(f"{output_dir}{name}-QMpH.svg")

iguana_data_agg.to_csv(f"{output_dir}{name}-scatter.tsv", sep="\t", index=None)
fully_agg.to_csv(f"{output_dir}{name}-QMpH.tsv", sep="\t", index=None)

plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{lmodern,amsmath,amssymb,sansmathfonts}'

watdiv_iguana_data_agg = iguana_data_agg.query("dataset == 'WatDiv'")
triplestore = 'T-hsi'
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


watdiv_iguana_data_agg[f'QPS relative to {triplestore}'] = watdiv_iguana_data_agg.apply(func, axis=1).values
watdiv_iguana_data_agg[f'QpS rel. to {triplestore}'] = np.log10(
    watdiv_iguana_data_agg[f'QPS relative to {triplestore}'])

watdiv_iguana_data_agg['triplestore'] = pd.Categorical(watdiv_iguana_data_agg['triplestore'],
                                                       categories=list(reversed(triplestores)),
                                                       ordered=True)

watdiv_query_names = pd.read_csv(data_dir.joinpath("watdiv_query_names.tsv"), sep="\t", index_col=False)
watdiv_iguana_data_agg = watdiv_iguana_data_agg.merge(watdiv_query_names)

watdiv_iguana_data_agg['name'] = pd.Categorical(watdiv_iguana_data_agg['name'],
                                                categories=watdiv_iguana_data_agg['name'].unique(),
                                                ordered=True)

r = (ggplot(watdiv_iguana_data_agg, aes('name', 'triplestore', fill=f'QpS rel. to {triplestore}'))
     + geom_tile()
     # + geom_text(aes(label=f'avgQPS relative to {triplestore}'), size=10)
     + xlab("Query")
     + ylab("Triple store")
     # + geom_text(mapping=aes(label='QMpH_rounded'), size=tiny_font_size, va='bottom', angle="45" )
     + theme_light()
     + theme(
            strip_background_x=element_text(color="#808080", ),
            strip_background=element_blank(),
            strip_text=element_blank(),
            panel_grid_major=element_blank(),
            panel_grid_minor=element_blank(),
            # legend_text=element_text('speedup (log10)'),
            # legend_position='none',
            # axis_text_y=element_text(weight="bold")
            axis_text_x=element_text(rotation=90, hjust=0.5),
            figure_size=(5.5, 1.25),
            legend_title_align='center',
            text=element_text(family="Latin Modern Sans", size=small_font_size)
        )
     + scale_fill_gradient2(low="#08519c", mid="#f7fbff", high="red",  # colors in the scale
                            midpoint=0,  # same midpoint for plots (mean of the range)
                            breaks=list(range(-4, 2)),  # breaks in the scale bar
                            labels=["$10^{{{} }}$".format(x) if x != 0 else "1" for x in range(-4, 2)],
                            limits=(1, -4.5),
                            na_value="black"
                            )
     )
name = "paper-heatmap-watdiv-rel-T-hsi"
save_as_pdf_pages([r], filename=f"{output_dir}{name}.pdf", bbox_inches="tight")
watdiv_iguana_data_agg.to_csv(f"{output_dir}{name}.tsv", sep="\t", index=None)
r.save(f"{output_dir}{name}.svg")
# print(q)
