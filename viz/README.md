# Visualisation of model outputs

The web-app detailed here is currently running at [nextstrain.github.io/forecasts-ncov/](https://nextstrain.github.io/forecasts-ncov/) and will visualise the lates available model run.
If you wish to visualise a local JSON file, it may be easiest to use [this drag-and-drop web app](https://nextstrain.github.io/forecasts-viz/).

## Prerequisites

The only software requirement is [Node.js](https://nodejs.org).
There are many ways to install this, but a common way is to use conda:

```bash
conda create -y -n node -c conda-forge nodejs
conda activate node
```

## Quickstart using "live" data from our S3 bucket

```bash
npm ci           # install JS dependencies
npm run build    # build the JS code
npm run preview  # open http://localhost:5173/forecasts-ncov/
```

This (single-page) app exists to visualise the model outputs to both generate static images as well as help development of the underlying visualisation library.
It is not intended to remain here long term; this will be added as a "normal" page of nextstrain.org once some technical hurdles are solved with that site.

All colors, display names etc are set within the JSON itself (see `/../scripts/modify-lineage-colours-and-order.py`).


## Using local JSONs

To begin with, ensure the quickstart (above) using live data is working as expected.

You will need two JSON files representing the clades and lineages analyses, and these will need to be located within the top-level results directory.
The paths to these files, relative to the results directory, are provided via the environment variables `VITE_CLADES_PATH` and `VITE_LINEAGES_PATH`. See `../README.md` for how to run the model pipeline which will be produce these files within `../results/`.

The command `npm run start:local` will both serve the website and provide access to the two JSON files defined via the env variables. For instance, using the default file paths produced by the model-run pipeline:


```bash
VITE_CLADES_PATH="gisaid/nextstrain_clades/global/mlr/YYYY-MM-DD_results.json" \
  VITE_LINEAGES_PATH="gisaid/pango_lineages/global/mlr/YYYY-MM-DD_results.json" \
  npm run start:local
```

Or, if your JSONs are `results/clades.json` and `results/lineages.json` then the command is:
```bash
VITE_CLADES_PATH="clades.json" VITE_LINEAGES_PATH="lineages.json" npm run start:local
```

## Development mode

Development mode is slightly slower than production mode but allows on-the-fly editing of the JavaScript code.

If you are using live (S3) data, run `npm run dev`.
If you are using local data, replace `npm run start:local` with `npm run start:local:dev`.


## Updating the viz library

We are using our generalised [@nextstrain/evofr-viz library](https://github.com/nextstrain/forecasts-viz) which is packed and
vendored here. To update the library:

1. In the library repo itself run `npm pack` to create a tarball
2. Move the tarball to this folder (`./viz`) so it will be committed, and remove the old one if necessary
3. `rm -rf node_modules package-lock.json`
4. `npm install <path_to_tarball>`

## Changing the styles of individual small-multiple graphs

You can provide style overrides to the `<PanelDisplay>` component (`./src/App.jsx`) to change selected styles on a case-by-case basis, which avoids having to update the underlying library. For instance (using the defaults for the frequency panel):

```diff
- <PanelDisplay graphType="r_t"/>
+ <PanelDisplay graphType="r_t" styles={{width: 250, height: 200, top: 5, right: 0, bottom: 20, left: 35}}/>
```

## Static image generation (no longer used)

```bash
# running from the viz directory
npm run build
node scripts/static-images.js
# images will be in ./figures
```

This is run via the `generate-static-model-viz` GitHub action of this repo.

You can `open ./example-static-images.html` to see an example HTML page where different image sizes are selected based on your screen size.

## Updating the GitHub pages site

A [GitHub Action](https://github.com/nextstrain/forecasts-ncov/blob/main/.github/workflows/deploy-viz-app.yaml) will automatically re-deploy the site whenever changes to files in this directory (`viz`) are committed to the main branch.
The GitHub pages site is available at [nextstrain.github.io/forecasts-ncov/](https://nextstrain.github.io/forecasts-ncov/).
