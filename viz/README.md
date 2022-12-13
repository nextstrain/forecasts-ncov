# Visualisation of model outputs

> _This is a work in progress!_

### Installation

* Everything should happen from the `viz` directory (where this file is)

* Create an enviornment with nodeJS and npm, e.g. 
`conda create -n <env-name> -c conda-forge nodejs=18`

```sh
npm install 
npm run start # dev mode
npm run build
```

Make local data available (temporary). (This is in `src/` because of a create-react-app restriction, BTW.)

```
mkdir -p src/data/
aws s3 cp s3://nextstrain-data-private/files/workflows/forecasts-ncov/global/renewal/2022-12-05_results.json.zst src/data/renewal.json.zst
aws s3 cp s3://nextstrain-data-private/files/workflows/forecasts-ncov/global/mlr/2022-12-05_results.json.zst src/data/mlr.json.zst
unzstd src/data/*.zst
rm src/data/*.zst
```

### Prior art

* https://github.com/blab/rt-from-frequency-dynamics/tree/master/results/omicron-countries-split
* https://github.com/blab/rt-from-frequency-dynamics/tree/master/results/pango-countries


### Todo

* finish (static-ish) viz
* export a react component we can use in gatsby, or render / serve SVG server-side?
* png + pdf export
* run on schedule, somewhere, to generate at each model run
