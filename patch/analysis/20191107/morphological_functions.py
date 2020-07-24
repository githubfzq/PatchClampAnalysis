import os.path
import warnings
import numpy as np
import pandas as pd
from scipy.stats import sem
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import neurom as nm
from neurom.view import view
from plot_helper import plot_unified_scale_grid, add_scalebar, to_save_figure
from analysis_functions import zero_padding, getAllFiles


class morpho_parser:

    selected_imaris_parameters = [
        "Filament Area (sum)",
        "Filament Dendrite Area (sum)",
        "Filament Dendrite Length (sum)",
        "Filament Dendrite Volume (sum)",
        "Filament Distance from Origin",
        "Filament Full Branch Depth",
        "Filament Full Branch Level",
        "Filament Length (sum)",
        "Filament No. Dendrite Branch Pts",
        "Filament No. Dendrite Segments",
        "Filament No. Dendrite Terminal Pts",
        "Filament Volume (sum)",
    ]

    def __init__(self, path_root=""):
        """Create morphological analysis processor.
        path_root: set path root for neuron morphology.
        Default path_root is empty, use default path_root."""
        if not (path_root):
            self.path_root = {
                "swc": "../../../reconstruction/traces/",
                "imaris": "../../../reconstruction/stat/",
            }
        else:
            self.path_root = path_root
        self.neurons = nm.load_neurons(self.path_root["swc"])
        self.files = {}
        self.files["swc"], _ = getAllFiles(self.path_root["swc"], ends="swc")
        self.files["imaris"] = {"stat": [], "soma": []}
        shollFiles, _ = getAllFiles(self.path_root["imaris"])
        for f in shollFiles:
            if "Detailed.csv" in f:
                # filter Detailed labled files
                if "soma" in f:
                    self.files["imaris"]["soma"].append(f)
                else:
                    self.files["imaris"]["stat"].append(f)
        # Cache imaris stat data
        self.imarisData = None
        # Cache depth parameter stat data computed
        self.depthData = None
        # Cache different dormain sholl intersection
        self.sholl_part_data = None
        # Cache computed result of sholl_prat_data
        self.sholl_part_stat = None
        # Cache all morphological parameters of neurons
        self.morphoData = dict(imaris=None, python=None, all=None)

    def plot_all_neurons(self, layout=None, to_save="", neurons=None, **kwargs):
        """Plot all neurons in array manner.
        layout: 1x2 tuple. including the row number and the colunm number.
        to_save: the file to save as. If left empty, not to save.
        **kwargs: parameters passed to `plot_multi_neuron()`"""
        if not neurons:
            neurons = self.neurons
        if not (layout):
            s = len(neurons)
            r = int(np.floor(np.sqrt(s)))
            c = int(np.ceil(s / r))
            layout = (r, c)
        plot_multi_neuron(neurons, layout, to_save, **kwargs)

    def plot_apical_upside(self, neurons=None, **kwargs):
        """Plot all neurons apical-upsided.
        neurons: neurons to plot.
        **kwargs: other parameters passed to `morpho_parser.plot_all_neurons()`."""
        if neurons is None:
            neurons = self.neurons
        roted = [apical_upside(tr) for tr in neurons]
        self.plot_all_neurons(neurons=roted, **kwargs)

    def get_sholl_parts_stat(self):
        """get sholl interactions including apical and basal parts with increaing 1 um for all neurons."""
        if self.sholl_part_data is None:
            result = pd.concat(map(lambda x: get_sholl_parts(x, 1), self.neurons))
            self.sholl_part_data = result
            return result
        else:
            return self.sholl_part_data

    def compute_sholl_parts_stat(self, sholl_dat=None):
        """Compute sholl analysis result including parts."""
        if self.sholl_part_stat is None:
            sholl_dat = self.get_sholl_parts_stat()
            shollPartsCompute = (
                zero_padding(sholl_dat, "intersections")
                .groupby(["label", "radius"])
                .agg([np.mean, sem])
            )
            shollPartsCompute.columns = [
                "_".join(x) for x in shollPartsCompute.columns.ravel()
            ]
            shollPartsCompute.reset_index(inplace=True)
            self.sholl_part_stat = shollPartsCompute
            return shollPartsCompute
        else:
            return self.sholl_part_stat

    def plot_sholl(self, sholl_part=True, to_save=""):
        """Plot sholl analysis of apical and basal parts.
        sholl_part: logical. plot domain or plot whole."""
        if not sholl_part:
            imarisData = self.get_imaris_stat()
            shollData = imarisData[
                imarisData.Variable == "Filament No. Sholl Intersections"
            ].loc[:, ["neuron_ID", "Radius", "Value"]]
            shollPlotData = (
                zero_padding(shollData, "Value")
                .groupby("Radius")
                .agg([np.mean, sem])
                .reset_index()
            )
            plt.plot(shollPlotData["Radius"], shollPlotData[("Value", "mean")])
            plt.fill_between(
                shollPlotData["Radius"],
                shollPlotData[("Value", "mean")] + shollPlotData[("Value", "sem")],
                shollPlotData[("Value", "mean")] - shollPlotData[("Value", "sem")],
                alpha=0.6,
            )
            plt.ylabel("Sholl intersections")
            plt.xlabel("$Radius\ (\mu m)$")
        else:
            dat = self.compute_sholl_parts_stat()
            dat = dat.pivot(
                index="radius",
                columns="label",
                values=["intersections_mean", "intersections_sem"],
            )
            plt.plot(
                dat.index,
                dat.intersections_mean.apical,
                dat.index,
                dat.intersections_mean.basal,
                label="",
            )
            ax1 = plt.fill_between(
                dat.index,
                dat.loc[:, ("intersections_mean", "apical")]
                + dat.loc[:, ("intersections_sem", "apical")],
                dat.loc[:, ("intersections_mean", "apical")]
                - dat.loc[:, ("intersections_sem", "apical")],
                alpha=0.6,
                label="apical",
            )
            ax2 = plt.fill_between(
                dat.index,
                dat.loc[:, ("intersections_mean", "basal")]
                + dat.loc[:, ("intersections_sem", "basal")],
                dat.loc[:, ("intersections_mean", "basal")]
                - dat.loc[:, ("intersections_sem", "basal")],
                alpha=0.6,
                label="basal",
            )
            plt.ylabel("Sholl intersections")
            plt.xlabel("$Radius\ (\mu m)$")
            plt.legend()
        if bool(to_save):
            to_save_figure(to_save)

    def get_imaris_stat(self):
        """Read morphological statistic data generated by Imaris software."""
        if self.imarisData is None:
            imarisData = pd.concat(
                map(read_demo_imaris_stat, self.files["imaris"]["stat"]), sort=True
            )
            self.imarisData = imarisData
            return imarisData
        else:
            return self.imarisData

    def get_depth_data(self):
        """Get branch depth data."""
        if self.depthData is None:
            imarisData = self.get_imaris_stat()
            depthData = (
                imarisData[imarisData.Variable == "Dendrite Branch Depth"]
                .loc[:, ["neuron_ID", "Depth", "Level", "Value"]]
                .groupby(["neuron_ID", "Depth"])
                .count()
                .reset_index()
                .drop("Level", axis=1)
                .rename({"Value": "counts"}, axis=1)
            )
            depthData.Depth = depthData.Depth.astype("int64")
            self.depthData = depthData
            return depthData
        else:
            return self.depthData

    def plot_depth(self, to_save=""):
        """Plot branch order distribution."""
        depthData = self.get_depth_data()
        depthPlotData = depthData.groupby("Depth").agg([np.mean, sem]).reset_index()
        plt.bar(
            depthPlotData["Depth"] + 1, depthPlotData[("counts", "mean")], alpha=0.6
        )
        plt.errorbar(
            depthPlotData["Depth"] + 1,
            depthPlotData[("counts", "mean")],
            depthPlotData[("counts", "sem")],
            linestyle="",
        )
        plt.ylabel("Number of filaments")
        plt.xlabel("Branch order")
        if bool(to_save):
            to_save_figure(to_save)

    def get_all_data(self, item='all'):
        """Get morphological parameters of all neuron for clustering analysis.
        item: {'all', 'imaris', 'python'}. Get only imaris data or stats of python, or all include."""
        if item == 'imaris':
            if self.morphoData['imaris'] is None:
                dat = self.get_imaris_stat()
                result = dat[dat["Variable"].isin(self.selected_imaris_parameters)][
                    ["neuron_ID", "Variable", "Value", "Unit"]
                ]
                result = result.pivot_table("Value", "neuron_ID", "Variable").reset_index()
                self.morphoData['imaris']=result.copy()
            else:
                result = self.morphoData['imaris'].copy()
        elif item == 'python':
            if self.morphoData['python'] is None:
                res_map=((neuron.name, *res) for neuron in self.neurons for res in  self.get_demo_morpho_parameter(neuron))
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    result = pd.DataFrame(res_map, columns=['reconstruction_ID', 'item', 'value'])
                result = result.pivot_table('value','reconstruction_ID','item')
                self.morphoData['python']=result.copy()
                return result
            else:
                result = self.morphoData['python'].copy()
        elif item == 'all':
            if self.morphoData['all'] is None:
                imaris_dat = self.get_all_data('imaris')
                imaris_dat.rename(columns={'neuron_ID':'reconstruction_ID'}, inplace=True)
                py_dat = self.get_all_data('python')
                py_dat = py_dat.reset_index()
                result = imaris_dat.merge(py_dat, 'outer', 'reconstruction_ID')
                self.morphoData['all']=result.copy()
            else:
                result = self.morphoData['all'].copy()
        return result

    def get_demo_morpho_parameter(self, neuron):
        """Get morphology parameters of a neuron (max_sholl_intercept).
        neuron: `Neuron` object."""
        def f1_1(name,part='all'):
            if part=='all':
                cur_res = nm.get(name, neuron).mean()
                cur_key = 'mean_' + name
            elif part=='apical':
                cur_res = nm.get(name, neuron, neurite_type=nm.APICAL_DENDRITE).mean()
                cur_key = 'mean_' + name + '(apical)'
            elif part=='basal':
                cur_res = nm.get(name, neuron, neurite_type=nm.BASAL_DENDRITE).mean()
                cur_key = 'mean_' + name + '(basal)'
            yield (cur_key, cur_res)
        def sholl_f(name, part='all'):
            par = {'all':nm.ANY_NEURITE, 'apical':nm.APICAL_DENDRITE,'basal':nm.BASAL_DENDRITE}
            freq = nm.get(name, neuron,neurite_type=par[part],step_size=1)
            suffix_ = {'all':'', 'apical':'(apical)', 'basal':'(basal)'}
            yield ('max_sholl_intercept'+suffix_[part], freq.max())
            yield ('max_sholl_intercept_radii'+suffix_[part], freq.argmax())
        def f2(name):
            cur_res = nm.get(name, neuron)[0]
            yield (name, cur_res)
        def f1(name):
            yield from f1_1(name)
            yield from f1_1(name, 'apical')
            yield from f1_1(name, 'basal')
        def f3(name):
            cur_res0=nm.get(name, neuron).sum()
            cur_res1=nm.get(name, neuron, neurite_type=nm.APICAL_DENDRITE).sum()
            cur_res2=nm.get(name, neuron, neurite_type=nm.BASAL_DENDRITE).sum()
            yield (name, cur_res0)
            yield (name+'(apical)', cur_res1)
            yield (name+'(basal)', cur_res2)
        def f4(name):
            yield from sholl_f(name)
            yield from sholl_f(name,'apical')
            yield from sholl_f(name,'basal')
        neurom_metric = {'local_bifurcation_angles':f1,
                    'neurite_lengths':f1,
                    'neurite_volume_density':f1,
                    'neurite_volumes':f1,
                    'number_of_bifurcations':f2,
                    'number_of_forking_points':f2,
                    'number_of_neurites':f2,
                    'number_of_sections':f2,
                    'number_of_sections_per_neurite':f2,
                    'number_of_segments':f2,
                    'number_of_terminations':f2,
                    'principal_direction_extents':f1,
                    'remote_bifurcation_angles':f1,
                    'section_areas':f1,
                        'section_bif_branch_orders':f1,
                        'section_branch_orders':f1,
                        'section_end_distances':f1,
                        'section_lengths':f1,
                        'total_length_per_neurite':f3,
                        'sholl_frequency':f4}
        for item, fun_ in neurom_metric.items():
            yield from fun_(item)
            
def read_demo_imaris_stat(file):
    """read one morphological data generated by Imaris software."""
    tb = pd.read_csv(file, skiprows=2, header=1)
    tb["neuron_ID"] = os.path.split(file)[-1].split("_Detailed.")[0]
    return tb[np.roll(tb.columns, 1)]


def get_sholl_parts(neuron, step_size):
    """return a dataframe including sholl frequency of apical and basal dendrites
    'step_size': the increasing radius (um)"""
    shollf1 = nm.get(
        "sholl_frequency",
        neuron,
        step_size=step_size,
        neurite_type=nm.NeuriteType.apical_dendrite,
    )
    shollf2 = nm.get(
        "sholl_frequency",
        neuron,
        step_size=step_size,
        neurite_type=nm.NeuriteType.basal_dendrite,
    )
    r1 = np.arange(len(shollf1)) * step_size
    r2 = np.arange(len(shollf2)) * step_size
    df1 = pd.DataFrame(
        {"radius": r1, "intersections": shollf1, "label": "apical", "id": neuron.name}
    )
    df2 = pd.DataFrame(
        {"radius": r2, "intersections": shollf2, "label": "basal", "id": neuron.name}
    )
    df = pd.concat([df1, df2])
    return df[df.intersections > 0]


def plot_multi_neuron(neurons, layout, to_save="", scalebar=(200,"$\mu m$"),fig_size=None):
    """Plot mutiple neurons in array manner.
    neurons: neurom.population.Population.
    layout: 1x2 tuple. including the row number and the colunm number.
    to_save: the file to save as. If left empty, not to save.
    fig_size: default: 2x2 inch multiple with layout."""
    if fig_size is None:
        fig_size=(2*layout[0], 2*layout[1])
    fig, axs = plt.subplots(*layout, figsize=fig_size)
    if layout[1]==1 and axs.ndim==1:
        axs=axs[:,np.newaxis]
    elif layout[0]==1 and axs.ndim==1:
        axs=axs[np.newaxis,:]
    for (ind, ax), neuron in zip(np.ndenumerate(np.array(axs)), neurons):
        view.plot_neuron(ax, neuron)
        ax.autoscale()
        ax.set_title("")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_axis_off()
    left = len(neurons) - layout[0] * layout[1]
    if left<0:
        for ax in axs.flat[left:]:
            ax.set_visible(False)
    plot_unified_scale_grid(fig, axs)
    add_scalebar(axs.flat[-1], scalebar[0], scalebar[1], fig)
    if bool(to_save):
        to_save_figure(to_save)


def apical_upside(neuron):
    """Put apical part of a neuron upside."""
    traned = nm.geom.translate(neuron, -neuron.soma.center)
    apic = [
        nrt for nrt in traned.neurites if nrt.type == nm.NeuriteType.apical_dendrite
    ]
    if apic:
        apic_center = np.mean(
            np.concatenate(list(map(lambda a: a.points[:, :3], apic))), axis=0
        )
        angle = np.pi / 2 - np.angle(np.complex(apic_center[0], apic_center[1]))
        roted = nm.geom.rotate(traned, (0, 0, 1), angle)
        return roted
    else:
        return traned

def plot_sholl_demo(neuron, step_size=30, label_dict=None, to_save=""):
    """Plot sholl analysis demo figure.
    Display the apical and basal part of a neuron, and concentric circles of sholl analysis.
    Args:
    - neuron: [neurom.fst._core.FstNeuron], a neuron object.
    - step_size: [int], the interval radius of the concentric circles.
    - label_dict: [dict], a dictionary indicate the position of label.
        the keys of dict are the label name, and the values are the (x, y) position.
        Default: {'Apical': (x1, y1), 'Basal': (x2, y2)}, where (x1,y1) and (x2,y2) are computed automatically.
    """
    neuron = apical_upside(neuron)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, aspect='equal')
    view.plot_neuron(ax, neuron)

    # draw circles
    center = neuron.soma.center[:2]
    _dist = np.linalg.norm(neuron.points[:,:2]-center, axis=1).max()
    radii = np.arange(step_size, _dist, step_size)
    patches = []
    for rad in radii:
        circle = mpatches.Circle(center, rad, fill=False, edgecolor='dimgray')
        patches.append(circle)
    p = PatchCollection(patches, match_original=True)
    ax.add_collection(p)

    # add labels
    if label_dict is None:
        apical_points = np.concatenate([x.points for x in nm.iter_neurites(neuron, filt=lambda t: t.type==nm.APICAL_DENDRITE)])
        apical_label_pos_xs = [apical_points[:,0].min()-center[0], apical_points[:,0].max()-center[0]]
        apical_label_pos_x = apical_label_pos_xs[0] if np.abs(apical_label_pos_xs[0])>np.abs(apical_label_pos_xs[1]) else apical_label_pos_xs[1]
        apical_label_pos_y = center[1]+(apical_points[:,1].max()-center[1])/2
        basal_points = np.concatenate([x.points for x in nm.iter_neurites(neuron, filt=lambda t: t.type==nm.BASAL_DENDRITE)])
        basal_label_pos_xs = [basal_points[:,0].min()-center[0],basal_points[:,0].max()-center[0]]
        basal_label_pos_x = basal_label_pos_xs[0] if np.abs(basal_label_pos_xs[0])>np.abs(basal_label_pos_xs[1]) else basal_label_pos_xs[1]
        basal_label_pos_y = center[1]+(basal_points[:,1].min()-center[1])/2
        label_dict = {'Apical':(apical_label_pos_x, apical_label_pos_y), 'Basal': (basal_label_pos_x, basal_label_pos_y)}

    for name,pos in label_dict.items():
        plt.annotate(name, pos)

    ax.autoscale()
    ax.set_axis_off()
    plt.title(None)
    if bool(to_save):
        to_save_figure(to_save)