import re
from collections import defaultdict
from functools import partial

import higlass
import numpy as np
import pandas as pd
from higlass.api import display, gather_plugin_urls

from .colors import color_collection
from .genome import mm10

TRACK_TABLE_PATH = "/browser/metadata/HiglassTracks.csv.gz"
CHROM_SIZES_PATH = "/browser/genome/mm10.main.chrom.sizes"

DEFAULT_HEIGHT_1D = 25
DEFAULT_HEIGHT_2D = 450

MODALITY_PALETTE = {
    # modality: {color key: value}
    "ATAC CPM": {"barFillColor": "#EF7D1A"},
    "mCH Frac": {"barFillColor": "#16499D"},
    "mCG Frac": {"barFillColor": "#36AE37"},
    "SMART CPM": {"barFillColor": "#7D4195"},
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
        server="https://higlass.io/api/v1",
        name="mm10 Chrom Sizes",
    ),
    "mm10_gene_annot": higlass.remote(
        uid="QDutvmyiSrec5nX4pA5WGQ",
        server="https://higlass.io/api/v1",
        name="mm10 Gene Annotations",
    ),
}


def string_to_list(string):
    """Split string to list by , or | or +"""
    if isinstance(string, str):
        return re.split("[,|+]", string)
    else:
        return string


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


def _get_view_height(view, nrows=1, adjust=150):
    total_height = 0
    for part in ["top", "center", "bottom"]:
        _tl = getattr(view.tracks, part, [])
        if _tl is not None:
            for _t in _tl:
                total_height += _t.height if _t.height is not None else 0
    total_height *= nrows
    total_height += adjust  # adjust for the top bar height
    return int(total_height)


class HiglassBrowser:
    def __init__(
        self,
        server,
        pos_1d="top",
        height_1d=DEFAULT_HEIGHT_1D,
        height_2d=DEFAULT_HEIGHT_2D,
        show_tooltip=True,
        show_mouse_position=True,
        toggle_position_search_box=True,
        default_modality_2d="Impute 10K",
        default_modality_1d=("mCH Frac", "mCG Frac", "ATAC CPM", "SMART CPM"),
    ):
        self.server = server

        # base parameters
        self.pos_1d = pos_1d
        self.height_1d = height_1d
        self.height_2d = height_2d
        self.default_modality_2d = default_modality_2d
        self.default_modality_1d = default_modality_1d
        self.default_track_options = {
            "showTooltip": show_tooltip,
            "showMousePosition": show_mouse_position,
        }
        self.toggle_position_search_box = toggle_position_search_box

        self.track_table = pd.read_csv(TRACK_TABLE_PATH, index_col=0)
        self.subclass_list = self.track_table["CellSubClass"].dropna().unique().tolist()
        self.chrom_sizes = pd.read_csv(CHROM_SIZES_PATH, index_col=0, sep="\t", header=None).squeeze()

        self.all_modality_1d = ["ATAC CPM", "SMART CPM", "mCH Frac", "mCG Frac", "Domain Boundary", "Compartment Score"]
        self.all_modality_2d = ["Impute 100K", "Impute 10K", "Raw 100K"]
        self.modality_list = self.all_modality_1d + self.all_modality_2d

        self.subclass_palette = color_collection.get_colors("subclass")

        self.modality_palette = MODALITY_PALETTE
        self.genome_tilesets = GENOME_TILESETS

    def _default_track_options(self, track_option_dict):
        if track_option_dict is None:
            track_option_dict = {}
        elif track_option_dict == "default":
            track_option_dict = self.default_track_options
        return track_option_dict

    def _get_genome_annot_tracks(self):
        chrom_size = self.genome_tilesets["mm10_chrom_size"].track("chromosome-labels", height=25)
        chrom_size.options.update(self.default_track_options)

        gene = self.genome_tilesets["mm10_gene_annot"].track("gene-annotations", height=100)
        gene.options.update(self.default_track_options)

        return [chrom_size, gene]

    def _region_to_global_coord(self, region, extend_fold=0.5, min_extend_length=500000):
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
        if not re.search(".+(:|-|,)\d+(:|-|,)\d+", region):
            region = mm10.get_gene_region(region)
        chrom, _, start, _, end = re.split("(:|-|,)", region.replace(" ", ""))

        chrom_order_index = self.chrom_sizes.index.tolist().index(chrom)
        global_chrom_start = self.chrom_sizes[:chrom_order_index].sum()

        global_start = global_chrom_start + int(start)
        global_end = global_chrom_start + int(end)

        length = global_end - global_start
        extend_length = max(abs(length) * extend_fold, min_extend_length)
        global_start -= extend_length
        global_end += extend_length

        if global_start > global_end:
            global_start, global_end = global_end, global_start

        global_start = max(0, global_start)
        global_end = min(self.chrom_sizes.sum(), global_end)
        return global_start, global_end

    def _has_tileset(self, ct_or_name, track_type=None):
        if ct_or_name in self.track_table.index:
            return True
        elif f"{ct_or_name} {track_type}" in self.track_table.index:
            return True
        else:
            return False

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
            try:
                row = self.track_table.loc[f"{ct_or_name} {track_type}"]
                name = f"{ct_or_name} {track_type}"
            except KeyError:
                raise KeyError(f"Cannot find {ct_or_name} {track_type} in track table")

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
        track_option_dict="default",
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
        center_track.options.update(self._default_track_options(track_option_dict))
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

            _opts = self._default_track_options(track_option_dict)
            _opts.update(self.modality_palette[_m])
            _t.options.update(_opts)

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
        track_option_dict="default",
    ):
        cell_types = string_to_list(cell_types)
        modality_1d = string_to_list(modality_1d)

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
                    track_option_dict=track_option_dict,
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
            # Arrange views and lock value scale
            max_cols = 4
            row_viewconf_list = []
            for row_start in range(0, len(views), max_cols):
                row_views = views[row_start : row_start + max_cols]
                row_viewconf = row_views[0].viewconf()
                for view in row_views[1:]:
                    row_viewconf = row_viewconf | view.viewconf()
                row_viewconf_list.append(row_viewconf)
            # multiple rows
            if len(row_viewconf_list) > 1:
                concat_viewconf = row_viewconf_list[0]
                for row_viewconf in row_viewconf_list[1:]:
                    concat_viewconf = concat_viewconf / row_viewconf
            else:
                concat_viewconf = row_viewconf_list[0]

            # Apply synchronization lock
            viewconf = concat_viewconf.locks(*locks)
        else:
            viewconf = views[0].viewconf()

        total_cols = len(views) * view_width
        nrows = int(np.ceil(total_cols / 12))
        viewconf_height = _get_view_height(viewconf.views[0], nrows=nrows)
        return viewconf, viewconf_height

    def multi_cell_type_1d_viewconf(
        self,
        cell_types,
        modalities=None,
        region=None,
        colorby="modality",
        groupby="modality",
        view_width=12,
        add_genome_track=True,
        track_option_dict="default",
    ):
        cell_types = string_to_list(cell_types)
        modalities = string_to_list(modalities)

        if modalities is None:
            modalities = self.default_modality_1d
        if groupby == "modality":
            groups = [(_ct, _m) for _m in modalities for _ct in cell_types]
        else:
            groups = [(_ct, _m) for _ct in cell_types for _m in modalities]

        all_tracks = defaultdict(list)

        if add_genome_track:
            _genome_tracks = self._get_genome_annot_tracks()
            all_tracks["top"].extend(_genome_tracks)

        track_option_dict = self._default_track_options(track_option_dict)

        _value_scale_lock_groups = defaultdict(list)  # key: modality, value: list of tracks
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
            _value_scale_lock_groups[_m].append(_t)

        view = higlass.view(*((v, k) for k, vl in all_tracks.items() for v in vl), width=view_width)
        if region is not None:
            coords = self._region_to_global_coord(region, min_extend_length=5000)
            view.domain(x=coords, inplace=True)

        viewconf = view.viewconf()
        viewconf_height = _get_view_height(view)

        print(_value_scale_lock_groups)
        # Lock value scale
        locks = []
        for modality, tracks in _value_scale_lock_groups.items():
            _other_tracks = [(view, t) for t in tracks[1:]]
            lock = higlass.lock((view, tracks[0]), *(_other_tracks))
            locks.append(lock)
        viewconf = viewconf.locks(*locks)
        return viewconf, viewconf_height

    def two_cell_type_diff_viewconf(
        self,
        cell_type_1,
        cell_type_2,
        add_genome_track=True,
        modality_2d=None,
        modality_1d=None,
        region1=None,
        region2=None,
        track_option_dict="default",
    ):
        if modality_1d is None:
            modality_1d = self.default_modality_1d
        if modality_2d is None:
            modality_2d = self.default_modality_2d

        modality_1d = string_to_list(modality_1d)

        # center tracks
        center1 = self.get_ct_tileset(ct_or_name=cell_type_1, track_type=modality_2d).track(
            "heatmap", height=self.height_2d
        )
        center1.options.update(self._default_track_options(track_option_dict))
        center2 = self.get_ct_tileset(ct_or_name=cell_type_2, track_type=modality_2d).track(
            "heatmap", height=self.height_2d
        )
        center2.options.update(self._default_track_options(track_option_dict))
        # divide center tracks
        center3 = higlass.divide(center1, center2).opts(
            colorRange=["blue", "white", "red"],
            valueScaleMin=0.1,
            valueScaleMax=10,
        )
        center3.options.update(self._default_track_options(track_option_dict))
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
            _opts = self._default_track_options(track_option_dict)
            _opts.update(self.modality_palette[_m])

            t1 = self.get_ct_tileset(ct_or_name=cell_type_1, track_type=_m).track("bar", height=self.height_1d)
            t1.options.update(_opts)
            track_1_list.append((t1, self.pos_1d))

            t2 = self.get_ct_tileset(ct_or_name=cell_type_2, track_type=_m).track("bar", height=self.height_1d)
            t2.options.update(_opts)
            track_2_list.append((t2, self.pos_1d))

            t3 = higlass.divide(t1, t2).opts(valueScaleMin=0.1, valueScaleMax=10)
            t3.type = "divergent-bar"
            t3.options.update(
                {
                    "valueScaling": "log",
                    "name": f"{_m} (left / right) - log scale",
                    "barFillColorTop": "red",
                    "barFillColorBottom": "blue",
                }
            )
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

        # set initial domain
        for v in viewconf.views:
            if region2 is None:
                region2 = region1
            if region1 is not None:
                v.domain(x=self._region_to_global_coord(region1), inplace=True)
                v.domain(y=self._region_to_global_coord(region2), inplace=True)

        viewconf_height = _get_view_height(viewconf.views[0])
        return viewconf, viewconf_height

    def loop_zoom_in_viewconf(
        self,
        cell_type,
        region1,
        region2=None,
        zoom_region1=None,
        zoom_region2=None,
        add_genome_track=True,
        modality_2d=None,
        modality_1d=None,
        track_option_dict="default",
    ):
        modality_1d = string_to_list(modality_1d)

        if modality_2d is None:
            modality_2d = self.default_modality_2d
        if modality_1d is None:
            modality_1d = self.default_modality_1d

        if region2 is None:
            region2 = region1
        if zoom_region1 is None:
            zoom_region1 = region1
        if zoom_region2 is None:
            zoom_region2 = zoom_region1

        domain_x = self._region_to_global_coord(region1)
        domain_y = self._region_to_global_coord(region2)
        zoom_domain_x = self._region_to_global_coord(zoom_region1, min_extend_length=5000)
        zoom_domain_y = self._region_to_global_coord(zoom_region2, min_extend_length=5000)

        coord_min = np.min([domain_x, domain_y])
        coord_max = np.max([domain_x, domain_y])
        v0_x = v0_y = (coord_min, coord_max)

        center_track = self.get_ct_tileset(ct_or_name=cell_type, track_type=modality_2d).track(
            "heatmap", height=self.height_2d
        )
        center_track.options.update(self._default_track_options(track_option_dict))

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

        def _add_opts(_t, _m):
            _opts = self._default_track_options(track_option_dict)
            _opts.update(self.modality_palette[_m])
            _t.options.update(_opts)
            return

        for _m in modality_1d:
            _t = self.get_ct_tileset(ct_or_name=cell_type, track_type=_m).track("bar", height=self.height_1d)
            _add_opts(_t, _m)
            left_track_list.append((_t, "top"))
            right_track_list.append((_t, "top"))

            # has to create a new track when plot in the same view
            _t = self.get_ct_tileset(ct_or_name=cell_type, track_type=_m).track("bar", height=self.height_1d)
            _add_opts(_t, _m)
            left_track_list.append((_t, "left"))
            _t = self.get_ct_tileset(ct_or_name=cell_type, track_type=_m).track("bar", height=self.height_1d)
            _add_opts(_t, _m)
            right_track_list.append((_t, "right"))

        # add genome tracks in the end so its on the outside
        right_track_list += genome_tracks_right[::-1]

        v0 = higlass.view(*left_track_list, width=6).domain(x=v0_x, y=v0_y)
        v1 = higlass.view(*right_track_list, width=6).domain(x=zoom_domain_x, y=zoom_domain_y)

        viewconf = v0.project(v1, "center") | v1

        viewconf_height = _get_view_height(v0)
        return viewconf, viewconf_height

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
        view_dict["trackSourceServers"] = [self.server, "https://higlass.io/api/v1"]
        for _v in view_dict["views"]:
            if self.toggle_position_search_box:
                # toggle position search box, change is inplace
                _v["genomePositionSearchBoxVisible"] = True
                _v["genomePositionSearchBox"] = {
                    "autocompleteServer": "https://higlass.io/api/v1",
                    "chromInfoServer": "https://higlass.io/api/v1",
                    "visible": True,
                    "chromInfoId": "mm10",
                }

        renderer = display.renderers.get()
        plugin_urls = [] if viewconf.views is None else gather_plugin_urls(viewconf.views)
        return renderer(view_dict, plugin_urls=plugin_urls)["text/html"]

    def get_higlass_html(self, layout_name, *args, **kwargs):
        # get viewconf function by layout name
        viewconf_func = getattr(self, f"{layout_name}_viewconf")

        viewconf, viewconf_height = viewconf_func(*args, **kwargs)
        html = self.render_viewconf_to_html(viewconf)
        return html, viewconf_height
