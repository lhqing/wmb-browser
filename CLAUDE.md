# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status: archive repo with a live deployment

This is the Whole Mouse Brain (WMB) Browser, a Plotly Dash app serving the snmC-seq3 / snm3C-seq adult mouse brain methylome + 3D genome atlas at <https://mousebrain.salk.edu>. Active development stopped in Oct 2024. Keep changes minimal and aimed at keeping the deployed app running. Do not modernize or refactor it.

## Production deployment (GCP)

- Project `ecker-bican`, VM `browser-small-0e06-head-cfxpcfmm-compute`, zone `us-west1-a`, `n2d-highmem-4` (4 vCPU / 32 GB). Its external IP must be the reserved "whole_mouse_brain" static address that `mousebrain.salk.edu` resolves to.
- The VM name follows SkyPilot's naming pattern (cluster `browser-small`). `sky-wmb-dev.yaml` is the template for this kind of VM (it specifies `n2d-highmem-16`, larger than the live one). It mounts GCS buckets, installs deps with conda/mamba (not poetry), and creates the HiGlass docker container.
- Request flow (see `nginx.conf` and `setup_nginx.md`):
  - `:80` redirects to https.
  - `:443` (nginx + certbot SSL) proxies to gunicorn at `127.0.0.1:8000`, which serves `index:server`.
  - `:8001` (nginx SSL) proxies to the HiGlass docker container `higlass-container` on `127.0.0.1:8989`. The app hardcodes this tile server as `https://mousebrain.salk.edu:8001/api/v1` in `backend/higlass_dash.py`.
- Restart sequence on the VM (gunicorn must run from inside `wmb_browser/`):

  ```bash
  sudo docker start higlass-container
  sudo systemctl restart nginx
  screen -R deploy
  cd wmb_browser && gunicorn -w 4 index:server -b 127.0.0.1:8000 --timeout 60 --access-logfile ~/access.log --error-logfile ~/error.log
  ```

- `Dockerfile` and `wmb_browser/apps/gunicorn.conf.py` are not part of the deployment. The Dockerfile is a cookiecutter leftover whose `CMD` points at a nonexistent `foo.py`.

## Runtime requirements (the app cannot start without these)

The backend builds module-level singletons at import time, so importing `wmb_browser.backend` (and therefore `index.py`) loads data and fails off the server:

- Hardcoded absolute paths under `/browser` (gs://hanqing-wmb-browser), `/cemba` (gs://hanqing-wmb-data-us-west1) and `/ref` (gs://hanqing-reference), mounted on the VM per `sky-wmb-dev.yaml`. These cover cell metadata and coords pickles, gene-by-cell zarr stores, `TotalPaletteDict.lib`, `HiglassTracks.csv.gz`, GENCODE vM23 and mm10 chrom sizes.
- `OPENAI_API_KEY` must be set in gunicorn's environment, because `backend/gpt_function_call.py` calls `OpenAI()` at import.
- Python packages used but not declared in `pyproject.toml`: `higlass-python` (`import higlass`), `openai` (v1 client), `gunicorn`.
- HiGlass tilesets are ingested, and the track uuid table `HiglassTracks.csv.gz` is generated, by notebooks that live in the GCS bucket (`notebooks/ingest_higlass.ipynb`, `metadata/generate_higlass_tracks.ipynb`), not in this repo. `notebooks/` here holds exploration and prep work, e.g. `prepare_palette_dict.ipynb` writes `TotalPaletteDict.lib`.

## Commands

```bash
cd wmb_browser && python index.py   # Dash debug server on :1234 (needs the data mounts above)
make install                        # poetry env + pre-commit hooks
make check                          # poetry lock --check, pre-commit, mypy, deptry
```

`index.py` imports `_app` as a top-level module (so the working directory must be `wmb_browser/`) and also imports `wmb_browser.*` (so the package must be installed or the repo root must be on `PYTHONPATH`).

There is no `tests/` directory, so `make test` and tox have nothing to run. Style is black + isort + flake8 at line length 120, enforced by pre-commit, and pre-commit.ci auto-fixes PRs. CI workflows trigger on `main`, but the default branch is `master`.

## Architecture

- `_app.py` creates the Dash `app` and `server` and holds the Google Analytics `index_string`. `index.py` adds the navbar and footer and routes on pathname: `/` or `/home`, `/dynamic_browser`, and `/download` (renders `assets/download_content.md`).
- **Plot strings are the central abstraction.** Each panel in `apps/dynamic_browser.py` is defined by a string of the form `dataset,plot_type,positional...,key=value...`. List values use `+`, e.g. `cell_types=CA3 Glut+Sst Gaba`. See `plot_examples` in that file.
  - `cemba_cell`: `continuous_scatter`, `categorical_scatter`, e.g. `cemba_cell,continuous_scatter,mc_all_tsne,gene_mch:Gad1`.
  - `higlass`: `multi_cell_type_2d`, `multi_cell_type_1d`, `two_cell_type_diff`, `loop_zoom_in`.
  - Shareable URLs chain strings: `/dynamic_browser?<string>?<string>`, up to `MAX_FIGURE_NUM = 8` panels. Layout configs can also be downloaded and uploaded as files.
- **Dispatch by name.** `_make_graph_from_string` parses the string, looks up the dataset singleton via `globals()` (star-imported from `wmb_browser.backend`) and calls `getattr(obj, plot_type)(index, *args, **kwargs)`, which returns `(dcc.Graph | Iframe, control_form)`. For HiGlass, `HiglassDash.get_higlass_and_control(layout=...)` resolves two methods by name: `{layout}_viewconf` in `backend/higlass.py` builds the HiGlass viewconf and renders it to HTML for `html.Iframe(srcDoc=...)`, and `_get_{layout}_control` in `backend/higlass_dash.py` builds the control form. Adding a plot type means adding these name-matched methods, adding the type to `ALL_PLOT_TYPES`, and adding update callbacks.
- **Pattern-matching IDs.** Components use dict IDs `{"index": i, "type": "<plot_type>-..."}`. The `MATCH`/`ALL` callbacks in `dynamic_browser.py` must use exactly the same `type` strings as the backend's components. Other callbacks sync pan/zoom across scatter panels that share a coord and show a cell's metadata card on click, using integer cell ids passed through `custom_data`.
- **`Dataset` (`backend/dataset.py`)** holds obs-by-var xarray matrices (lazy zarr), a metadata DataFrame and named 2D coords. A var matrix can be keyed by a coarser metadata level (e.g. `gene_rna` by `CellGroup`) and is mapped down to cells through metadata. `CEMBAsnmCCells` (`backend/cemba_cell.py`) is the concrete subclass. Color tokens like `gene_mch:Gad1` select a var set plus a gene, and gene names are converted to Ensembl ids through `backend/genome.py` (`mm10`).
- **Palettes.** `backend/colors.py` `color_collection.get_colors(name)`, with `_palette_alias`. A categorical scatter needs a palette for its color variable.
- **GPT mode.** When the ChatGPT switch is on and a string fails to parse, `chatgpt_string_to_args_and_kwargs` sends it to OpenAI (`gpt-4o-mini-2024-07-18`, legacy `functions`/`function_call` API) with two function schemas. It maps the result back to dataset, plot type and kwargs, using the `alias` dict to translate user-facing names to internal ones.
