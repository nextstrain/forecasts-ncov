# Visualisation of model outputs

> _This is a work in progress!_

### Installation

* Everything should happen from the `viz` directory (where this file is)

* Create an enviornment with nodeJS and npm, e.g. 
`conda create -n <env-name> -c conda-forge nodejs=18`

```sh
npm install 
npm run start # dev mode
```

### Where are model data sourced from?

By default, the model data is fetched from `https://nextstrain-data.s3.amazonaws.com/files/workflows/forecasts-ncov/trial/2022-12-18_results.json` (TODO - this is temporary, until we have a latest endpoint).
This can be changed via the following environment variable:

* If you wish to use a HTTPS endpoint, run `REACT_APP_MODEL_ENDPOINT="https://..." npm run start`. Browser-compatible MIME types will be used but note this doesn't yet include zstd.

* If you wish to use a local JSON, provision the files and serve them via a simple server (see below), then use `REACT_APP_MODEL_ENDPOINT="http://localhost:8000/renewal.json" npm run start`

How to make local data available (note that `/data` is gitignored):

```sh
# provision the files
mkdir -p data/
aws s3 cp s3://nextstrain-data-private/files/workflows/forecasts-ncov/global/renewal/2022-12-05_results.json.zst src/data/renewal.json.zst
aws s3 cp s3://nextstrain-data-private/files/workflows/forecasts-ncov/global/mlr/2022-12-05_results.json.zst src/data/mlr.json.zst
unzstd data/*.zst
rm data/*.zst
# serve them over localhost (port 8000 by default)
cd data
python -m http.server
```

> Note that we cannot currently use the zstd encodings. There is a library to decompress this in the browser (https://github.com/bokuweb/zstd-wasm) but it requires webpack modifications. For the time being, I've chosen to use gzip encodings. 

### Regenerating the png images in `figures`

`node scripts/static-images.js`

These images are referenced in `./report.md`

### Prior art

* https://github.com/blab/rt-from-frequency-dynamics/tree/master/results/omicron-countries-split
* https://github.com/blab/rt-from-frequency-dynamics/tree/master/results/pango-countries

### Todo

* export a react component we can use in gatsby, or render / serve SVG server-side?
* run on schedule, somewhere, to generate at each model run
* URL inspection to choose model JSON path

