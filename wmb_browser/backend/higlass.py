import re
from collections import defaultdict
from functools import partial

import higlass
import numpy as np
import pandas as pd
from higlass.api import display, gather_plugin_urls

from .colors import color_collection

TRACK_TABLE_PATH = "/browser/metadata/HiglassTracks.csv.gz"
CHROM_SIZES_PATH = "/browser/genome/mm10.main.chrom.sizes"

MODALITY_PALETTE = {
    # modality: {color key: value}
    "ATAC CPM": {"barFillColor": "#1f77b4"},
    "mCH Frac": {"barFillColor": "#16499D"},
    "mCG Frac": {"barFillColor": "#36AE37"},
    "Domain Boundary": {"barFillColor": "#E71F19"},
    "Compartment Score": {
        "barFillColorTop": "#E71F19",
        "barFillColorBottom": "#16499D",
    },  # plus strand is red (A comp), minus strand is blue (B comp)
    # "Impute 100K": "",
    # "Impute 10K": "",
    # "Raw 100K": "",
}

GENOME_TILESETS = {
    "mm10_chrom_size": higlass.remote(
        uid="EtrWT0VtScixmsmwFSd7zg",
        server="http://higlass.io/api/v1",
        name="mm10 Chrom Sizes",
    ),
    "mm10_gene_annot": higlass.remote(
        uid="QDutvmyiSrec5nX4pA5WGQ",
        server="http://higlass.io/api/v1",
        name="mm10 Gene Annotations",
    ),
}


def _auto_view_width(ncts):
    if ncts <= 1:
        view_width = 12
    elif ncts == 2:
        view_width = 6
    elif ncts == 3:
        view_width = 4
    else:
        view_width = 3
    return view_width


class HiglassBrowser:
    def __init__(
        self,
        server,
        pos_1d="top",
        height_1d=25,
        height_2d=500,
        show_tooltip=True,
        show_mouse_position=True,
        toggle_position_search_box=True,
        default_modality_2d="Impute 10K",
        default_modality_1d=("mCH Frac", "mCG Frac", "ATAC CPM"),
    ):
        self.server = server

        # base parameters
        self.pos_1d = pos_1d
        self.height_1d = height_1d
        self.height_2d = height_2d
        self.default_modality_2d = default_modality_2d
        self.default_modality_1d = default_modality_1d
        self._default_track_options = {
            "showTooltip": show_tooltip,
            "showMousePosition": show_mouse_position,
        }
        self.toggle_position_search_box = toggle_position_search_box

        self.track_table = pd.read_csv(TRACK_TABLE_PATH, index_col=0)
        self.chrom_sizes = pd.read_csv(CHROM_SIZES_PATH, index_col=0, sep="\t", header=None).squeeze()

        self.all_modality_1d = ["ATAC CPM", "mCH Frac", "mCG Frac", "Domain Boundary", "Compartment Score"]
        self.all_modality_2d = ["Impute 100K", "Impute 10K", "Raw 100K"]

        self.subclass_palette = color_collection.get_colors("subclass")

        self.modality_palette = MODALITY_PALETTE
        self.genome_tilesets = GENOME_TILESETS

    def _default_track_options(self, track_option_dict):
        if track_option_dict is None:
            track_option_dict = {}
        elif track_option_dict == "default":
            track_option_dict = self._default_track_options
        return track_option_dict

    def _get_genome_annot_tracks(self):
        chrom_size = self.genome_tileset["mm10_chrom_size"].track("chromosome-labels", height=25)
        gene = self.genome_tileset["mm10_gene_annot"].track("gene-annotations", height=100)
        return [chrom_size, gene]

    def _region_to_global_coord(self, region, extend_fold=0.5):
        """
        Turn a region string into global number coordinates

        Parameters
        ----------
        region : str
            Region string, e.g. chr1:1000-2000
        chrom_sizes : pd.Series
            Chromosome sizes
        extend_fold : float, optional
            Extend the region by this fold, by default 0.5

        Returns
        -------
        global_start, global_end
            Global coordinates
        """
        chrom, _, start, _, end = re.split("(:|-|,)", region.replace(" ", ""))

        chrom_order_index = self.chrom_sizes.index.tolist().index(chrom)
        global_chrom_start = self.chrom_sizes[:chrom_order_index].sum()

        global_start = global_chrom_start + int(start)
        global_end = global_chrom_start + int(end)

        length = global_end - global_start
        extend_length = max(abs(length) * extend_fold, 5000)
        global_start -= extend_length
        global_end += extend_length

        if global_start > global_end:
            global_start, global_end = global_end, global_start

        global_start = max(0, global_start)
        global_end = min(self.chrom_sizes.sum(), global_end)
        return global_start, global_end

    def get_ct_tileset(self, ct_or_name, track_type=None):
        """
        Get a cell type tileset

        Parameters
        ----------
        ct_or_name : str
            Cell type name or track name
        track_type : str, optional
            Track type, by default None

        Returns
        -------
        tileset
            Tileset object
        """
        try:
            row = self.track_table.loc[ct_or_name]
            name = ct_or_name
        except KeyError:
            row = self.track_table.loc[f"{ct_or_name} {track_type}"]
            name = f"{ct_or_name} {track_type}"

        uuid = row["uuid"]

        tileset = higlass.remote(uid=uuid, server=self.server, name=name)
        return tileset

    def _get_cell_type_2d_view(
        self,
        cell_type,
        modality_2d=None,
        modality_1d=None,
        add_genome_track=True,
        view_width=6,
    ):
        """Get a 2D view for a given cell type"""
        if modality_2d is None:
            modality_2d = self.default_modality_2d
        if modality_1d is None:
            modality_1d = self.default_modality_1d

        _get_tileset = partial(self.get_ct_tileset, ct_or_name=cell_type)

        all_tracks = defaultdict(list)

        # center 2D
        center_tileset = _get_tileset(track_type=modality_2d)
        center_track = center_tileset.track("heatmap", height=self.height_2d)
        all_tracks["center"].append(center_track)

        # top annot
        if add_genome_track:
            _genome_tracks = self._get_genome_annot_tracks()
            all_tracks["top"].extend(_genome_tracks)

        # other 1d modalities
        for _m in modality_1d:
            if _m == "Compartment Score":
                _tt = "divergent-bar"
            else:
                _tt = "bar"
            _t = _get_tileset(track_type=_m).track(_tt, height=self.height_1d)
            all_tracks[self.pos_1d].append(_t)

        view = higlass.view(*((v, k) for k, vl in all_tracks.items() for v in vl), width=view_width)
        return view

    def multi_cell_type_2d_viewconf(
        self,
        cell_types,
        modality_2d=None,
        modality_1d=None,
        add_genome_track=True,
        region1=None,
        region2=None,
        view_width="auto",
    ):
        if view_width == "auto":
            view_width = _auto_view_width(len(cell_types))

        views = []
        for ct in cell_types:
            views.append(
                self._get_cell_type_2d_view(
                    cell_type=ct,
                    modality_2d=modality_2d,
                    modality_1d=modality_1d,
                    add_genome_track=add_genome_track,
                    view_width=view_width,
                )
            )

        # set initial domain
        for v in views:
            if region2 is None:
                region2 = region1
            if region1 is not None:
                v.domain(x=self._region_to_global_coord(region1), inplace=True)
                v.domain(y=self._region_to_global_coord(region2), inplace=True)

        if len(cell_types) > 1:
            locks = []

            # Lock zoom & location for each View
            view_lock = higlass.lock(*views)
            locks.append(view_lock)

            # Lock value scale
            v0 = views[0]
            pos_attrs = ["center", "top", "bottom", "left", "right"]
            for pos in pos_attrs:
                v0_tracks = getattr(v0.tracks, pos)
                if v0_tracks is None:
                    continue
                for i, v0_track in enumerate(v0_tracks):
                    _other_tracks = [(v, getattr(v.tracks, pos)[i]) for v in views[1:]]
                    lock = higlass.lock((v0, v0_track), *(_other_tracks))
                    locks.append(lock)

            # Concatenate Views side-by-side
            concat_viewconf = views[0].viewconf()
            for view in views[1:]:
                concat_viewconf = concat_viewconf | view

            # Apply synchronization lock
            viewconf = concat_viewconf.locks(*locks)
        else:
            viewconf = views[0].viewconf()
        return viewconf

    def multi_cell_type_1d_viewconf(
        self,
        cell_types,
        modalitys=None,
        colorby="modality",
        groupby="modality",
        view_width=12,
        add_genome_track=True,
        track_option_dict="default",
    ):
        if modalitys is None:
            modalitys = self.default_modality_1d
        if groupby == "modality":
            groups = [(_ct, _m) for _m in modalitys for _ct in cell_types]
        else:
            groups = [(_ct, _m) for _ct in cell_types for _m in modalitys]

        all_tracks = defaultdict(list)

        if add_genome_track:
            _genome_tracks = self._get_genome_annot_tracks()
            all_tracks["top"].extend(_genome_tracks)

        track_option_dict = self._default_track_options(track_option_dict)

        for _ct, _m in groups:
            if _m == "Compartment Score":
                _tt = "divergent-bar"
            else:
                _tt = "bar"
            _t = self.get_ct_tileset(ct_or_name=_ct, track_type=_m).track(_tt, height=self.height_1d)

            # add track colors by modality or subclass
            if colorby == "modality":
                modality = " ".join(_t.options["name"].split(" ")[-2:])
                try:
                    color_opt = self.modality_palette[modality]
                    track_option_dict.update(color_opt)
                except KeyError:
                    pass
            elif colorby == "subclass":
                modality = " ".join(_t.options["name"].split(" ")[-2:])
                subclass = " ".join(_t.options["name"].split(" ")[:-2])
                try:
                    color = self.subclass_palette[subclass]
                    if modality == "Compartment Score":
                        track_option_dict.update({"barFillColorTop": color, "barFillColorBottom": color})
                    else:
                        track_option_dict.update({"barFillColor": color})
                except KeyError:
                    pass
            else:
                raise ValueError(f"Unknown color_by {colorby}, only support 'modality' or 'subclass'")

            _t.options.update(track_option_dict)
            all_tracks[self.pos_1d].append(_t)

        view = higlass.view(*((v, k) for k, vl in all_tracks.items() for v in vl), width=view_width)
        return view.viewconf()

    def two_cell_type_diff_viewconf(
        self,
        cell_type_1,
        cell_type_2,
        add_genome_track=True,
        modality_2d=None,
        modality_1d=None,
    ):
        # center tracks
        center1 = self.get_ct_tileset(ct_or_name=cell_type_1, track_type=modality_2d).track(
            "heatmap", height=self.height_2d
        )
        center2 = self.get_ct_tileset(ct_or_name=cell_type_2, server=self.server, track_type=modality_2d).track(
            "heatmap", height=self.height_2d
        )
        # divide center tracks
        center3 = higlass.divide(center1, center2).opts(
            colorRange=["blue", "white", "red"],
            valueScaleMin=0.1,
            valueScaleMax=10,
        )
        center3.options["name"] = f"{modality_2d} (left / right) - log scale"

        # add genome track
        if add_genome_track:
            genome_tracks = [(t, "top") for t in self._get_genome_annot_tracks()]
        else:
            genome_tracks = []

        # 1d tracks
        track_1_list = [(center1, "center")] + genome_tracks
        track_2_list = [(center2, "center")] + genome_tracks
        track_3_list = [(center3, "center")] + genome_tracks
        for _m in modality_1d:
            t1 = self.get_ct_tileset(ct_or_name=cell_type_1, track_type=_m).track("bar", height=self.height_1d)
            track_1_list.append((t1, self.pos_1d))
            t2 = self.get_ct_tileset(ct_or_name=cell_type_2, track_type=_m).track("bar", height=self.height_1d)
            track_2_list.append((t2, self.pos_1d))
            t3 = higlass.divide(t1, t2).opts(valueScaleMin=0.1, valueScaleMax=10)
            t3.type = "divergent-bar"
            t3.options["valueScaling"] = "log"
            t3.options["name"] = f"{_m} (left / right) - log scale"
            track_3_list.append((t3, self.pos_1d))

        # views
        v1 = higlass.view(*track_1_list, width=4)
        v2 = higlass.view(*track_2_list, width=4)
        v3 = higlass.view(*track_3_list, width=4)

        locks = []

        # lock zoom & location
        lock = higlass.lock(v1, v2, v3)
        locks.append(lock)

        # Lock value scale
        pos_attrs = ["center", "top", "bottom", "left", "right"]
        for pos in pos_attrs:
            v1_tracks = getattr(v1.tracks, pos)
            if v1_tracks is None:
                continue
            v2_tracks = getattr(v2.tracks, pos)
            for v1_track, v2_track in zip(v1_tracks, v2_tracks):
                lock = higlass.lock((v1, v1_track), (v2, v2_track))
                locks.append(lock)

        # view locks
        viewconf = (v1 | v3 | v2).locks(*locks)
        return viewconf

    def loop_zoom_in_viewconf(
        self,
        cell_type,
        region1,
        region2,
        add_genome_track=True,
        modality_2d=None,
        modality_1d=None,
    ):
        if modality_2d is None:
            modality_2d = self.default_modality_2d
        if modality_1d is None:
            modality_1d = self.default_modality_1d

        domain_x = self._region_to_global_coord(region1)
        domain_y = self._region_to_global_coord(region2)

        coord_min = np.min([domain_x, domain_y])
        coord_max = np.max([domain_x, domain_y])
        v0_x = v0_y = (coord_min, coord_max)

        center_track = self.get_ct_tileset(ct_or_name=cell_type, track_type=modality_2d).track(
            "heatmap", height=self.height_2d
        )

        # add genome track
        if add_genome_track:
            genome_tracks_top = [(t, "top") for t in self._get_genome_annot_tracks()]
            genome_tracks_left = [(t, "left") for t in self._get_genome_annot_tracks()]
            genome_tracks_right = [(t, "right") for t in self._get_genome_annot_tracks()]
        else:
            genome_tracks_top = []
            genome_tracks_left = []
            genome_tracks_right = []

        left_track_list = [(center_track, "center")] + genome_tracks_top + genome_tracks_left  # global view
        right_track_list = [
            (center_track, "center")
        ] + genome_tracks_top  # zoom in view, add genome tracks in the end so its on the outside

        for _m in modality_1d:
            _t = self.get_ct_tileset(ct_or_name=cell_type, track_type=_m).track("bar", height=self.height_1d)
            left_track_list.append((_t, "top"))
            right_track_list.append((_t, "top"))

            # has to create a new track when plot in the same view
            _t = self.get_ct_tileset(ct_or_name=cell_type, track_type=_m).track("bar", height=self.height_1d)
            left_track_list.append((_t, "left"))
            _t = self.get_ct_tileset(ct_or_name=cell_type, track_type=_m).track("bar", height=self.height_1d)
            right_track_list.append((_t, "right"))

        # add genome tracks in the end so its on the outside
        right_track_list += genome_tracks_right[::-1]

        v0 = higlass.view(*left_track_list, width=6).domain(x=v0_x, y=v0_y)
        v1 = higlass.view(*right_track_list, width=6).domain(x=domain_x, y=domain_y)

        viewconf = v0.project(v1, "center") | v1
        return viewconf

    def render_viewconf_to_html(self, viewconf):
        """
        Render a viewconf to html

        Parameters
        ----------
        viewconf : higlass.View or higlass.Viewconf
            Higlass view or viewconf
        """
        if isinstance(viewconf, higlass.api.View):
            viewconf = viewconf.viewconf()

        view_dict = viewconf.dict()
        view_dict["trackSourceServers"] = [self.server, "http://higlass.io/api/v1"]
        for _v in view_dict["views"]:
            if self.toggle_position_search_box:
                # toggle position search box, change is inplace
                _v["genomePositionSearchBoxVisible"] = True
                _v["genomePositionSearchBox"] = {
                    "autocompleteServer": "http://higlass.io/api/v1",
                    "chromInfoServer": "http://higlass.io/api/v1",
                    "visible": True,
                    "chromInfoId": "mm10",
                }

        renderer = display.renderers.get()
        plugin_urls = [] if viewconf.views is None else gather_plugin_urls(viewconf.views)
        return renderer(view_dict, plugin_urls=plugin_urls)["text/html"]

    def get_higlass_html(self, layout_name, *args, **kwargs):
        # get viewconf function by layout name
        viewconf_func = getattr(self, f'{layout_name}_viewconf')

        viewconf = viewconf_func(*args, **kwargs)
        html = self.render_viewconf_to_html(viewconf)
        return html
