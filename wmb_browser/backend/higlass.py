import re
import pandas as pd
from functools import partial
from collections import defaultdict
import higlass
from higlass.api import display, gather_plugin_urls
from .colors import color_collection

track_table = pd.read_csv("/browser/metadata/HiglassTracks.csv.gz", index_col=0)
chrom_sizes = pd.read_csv("/browser/genome/mm10.main.chrom.sizes", index_col=0, sep="\t", header=None).squeeze()

modality_1d = ["ATAC CPM", "mCH Frac", "mCG Frac", "Domain Boundary", "Compartment Score"]
modality_2d = ["Impute 100K", "Impute 10K", "Raw 100K"]

subclass_palette = color_collection.get_colors("subclass")

modality_palette = {
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

genome_tileset = {
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


def _add_genome_annot_tracks(all_tracks):
    _t = genome_tileset["mm10_chrom_size"].track("chromosome-labels", height=25)
    all_tracks["top"].append(_t)
    _t = genome_tileset["mm10_gene_annot"].track("gene-annotations", height=100)
    all_tracks["top"].append(_t)
    return all_tracks


def _default_track_options(track_option_dict):
    if track_option_dict is None:
        track_option_dict = {}
    elif track_option_dict == "default":
        track_option_dict = {"showTooltip": True, "showMousePosition": True}
    return track_option_dict


def _region_to_global_coord(region, chrom_sizes=chrom_sizes, extend_fold=0.5):
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

    chrom_order_index = chrom_sizes.index.tolist().index(chrom)
    global_chrom_start = chrom_sizes[:chrom_order_index].sum()

    global_start = global_chrom_start + int(start)
    global_end = global_chrom_start + int(end)

    length = global_end - global_start
    extend_length = max(abs(length) * extend_fold, 5000)
    global_start -= extend_length
    global_end += extend_length

    if global_start > global_end:
        global_start, global_end = global_end, global_start

    global_start = max(0, global_start)
    global_end = min(chrom_sizes.sum(), global_end)
    return global_start, global_end


def get_ct_tileset(ct_or_name, server, track_type=None):
    """
    Get a cell type tileset

    Parameters
    ----------
    ct_or_name : str
        Cell type name or track name
    server : str
        Server address
    track_type : str, optional
        Track type, by default None

    Returns
    -------
    tileset
        Tileset object
    """
    try:
        row = track_table.loc[ct_or_name]
        name = ct_or_name
    except KeyError:
        row = track_table.loc[f"{ct_or_name} {track_type}"]
        name = f"{ct_or_name} {track_type}"

    uuid = row["uuid"]

    tileset = higlass.remote(uid=uuid, server=server, name=name)
    return tileset


def _get_cell_type_2d_view(
    cell_type,
    server,
    modality_2d,
    modality_1d,
    pos_1d,
    add_genome_track,
    height_1d=25,
    height_2d=500,
    view_width=6,
):
    """
    Get a 2D view for a given cell type

    Parameters
    ----------
    cell_type : str
        Cell type name
    server : str
        Server address
    modality_2d : str
        2D modality
    modality_1d : tuple, optional
        1D modalities
    pos_1d : str, optional
        1D track position
    add_genome_track : bool, optional
        Whether to add choromosome and gene annotation tracks
    height_1d : int, optional
        1D track height, by default 25
    height_2d : int, optional
        2D track height, by default 500
    view_width : int, optional
        View width, by default 6

    Returns
    -------
    view
        Higlass view
    """
    _get_tileset = partial(get_ct_tileset, ct_or_name=cell_type, server=server)

    all_tracks = defaultdict(list)

    # center 2D
    center_tileset = _get_tileset(track_type=modality_2d)
    center_track = center_tileset.track("heatmap", height=height_2d)
    all_tracks["center"].append(center_track)

    # top annot
    if add_genome_track:
        all_tracks = _add_genome_annot_tracks(all_tracks)

    # other 1d modalities
    if modality_1d is None:
        modality_1d = []
    for _m in modality_1d:
        if _m == "Compartment Score":
            _tt = "divergent-bar"
        else:
            _tt = "bar"
        _t = _get_tileset(track_type=_m).track(_tt, height=height_1d)
        all_tracks[pos_1d].append(_t)

    view = higlass.view(*((v, k) for k, vl in all_tracks.items() for v in vl), width=view_width)
    return view


def multi_cell_type_2d_viewconf(
    cell_types,
    server,
    modality_2d="Impute 10K",
    modality_1d=("mCH Frac", "mCG Frac", "ATAC CPM"),
    pos_1d="top",
    add_genome_track=True,
    height_1d=25,
    height_2d=500,
    view_width="auto",
):
    if view_width == "auto":
        view_width = _auto_view_width(len(cell_types))
    views = []
    for ct in cell_types:
        views.append(
            _get_cell_type_2d_view(
                cell_type=ct,
                server=server,
                modality_2d=modality_2d,
                modality_1d=modality_1d,
                pos_1d=pos_1d,
                add_genome_track=add_genome_track,
                height_1d=height_1d,
                height_2d=height_2d,
                view_width=view_width,
            )
        )

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


def _get_cell_types_1d_view(
    cell_types, modalitys, groupby, server, pos_1d, height_1d, view_width, add_genome_track, track_option_dict, color_by
):
    if groupby == "modality":
        groups = [(_ct, _m) for _m in modalitys for _ct in cell_types]
    else:
        groups = [(_ct, _m) for _ct in cell_types for _m in modalitys]

    all_tracks = defaultdict(list)

    if add_genome_track:
        all_tracks = _add_genome_annot_tracks(all_tracks)

    track_option_dict = _default_track_options(track_option_dict)

    for _ct, _m in groups:
        if _m == "Compartment Score":
            _tt = "divergent-bar"
        else:
            _tt = "bar"
        _t = get_ct_tileset(ct_or_name=_ct, track_type=_m, server=server).track(_tt, height=height_1d)

        # add track colors by modality or subclass
        if color_by == "modality":
            modality = " ".join(_t.options["name"].split(" ")[-2:])
            try:
                color_opt = modality_palette[modality]
                track_option_dict.update(color_opt)
            except KeyError:
                pass
        elif color_by == "subclass":
            modality = " ".join(_t.options["name"].split(" ")[-2:])
            subclass = " ".join(_t.options["name"].split(" ")[:-2])
            try:
                color = subclass_palette[subclass]
                if modality == "Compartment Score":
                    track_option_dict.update({"barFillColorTop": color, "barFillColorBottom": color})
                else:
                    track_option_dict.update({"barFillColor": color})
            except KeyError:
                pass
        else:
            raise ValueError(f"Unknown color_by {color_by}, only support 'modality' or 'subclass'")

        _t.options.update(track_option_dict)
        all_tracks[pos_1d].append(_t)

    view = higlass.view(*((v, k) for k, vl in all_tracks.items() for v in vl), width=view_width)
    return view


def multi_cell_type_1d_viewconf(
    cell_types,
    server,
    modality_1d=("mCH Frac", "mCG Frac", "ATAC CPM"),
    groupby="modality",
    pos_1d="top",
    add_genome_track=True,
    height_1d=25,
    view_width=12,
    color_by="modality",
    track_option_dict="default",
):
    view = _get_cell_types_1d_view(
        cell_types=cell_types,
        modalitys=modality_1d,
        groupby=groupby,
        server=server,
        pos_1d=pos_1d,
        height_1d=height_1d,
        view_width=view_width,
        add_genome_track=add_genome_track,
        color_by=color_by,
        track_option_dict=track_option_dict,
    )
    return view.viewconf()


def render_viewconf_to_html(viewconf, server, region1=None, region2=None):
    """
    Render a viewconf to html

    Parameters
    ----------
    viewconf : higlass.View or higlass.Viewconf
        Higlass view or viewconf
    region1 : str, optional
        Zoom to region 1 (e.g. chr1:1000-2000) in the x axis, by default None
    region2 : str, optional
        Zoom to region 2 (e.g. chr1:1000-2000) in the y axis, by default None
    """
    if isinstance(viewconf, higlass.api.View):
        viewconf = viewconf.viewconf()

    view_dict = viewconf.dict()
    view_dict["trackSourceServers"] = [server, "http://higlass.io/api/v1"]
    for _v in view_dict["views"]:
        # set view point
        if region1 is not None:
            _xs, _xe = _region_to_global_coord(region1)
            _v["initialXDomain"] = [_xs, _xe]
            if region2 is None:
                region2 = region1
            _ys, _ye = _region_to_global_coord(region2)
            _v["initialYDomain"] = [_ys, _ye]

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
