# Visualisation of model outputs

> _This is a work in progress!_

Quickstart:

```
npm ci
npm run dev # open http://localhost:5173
```

This (single-page) app exists to visualise the model outputs to both generate static images as well as help development of the underlying visualisation library.
It is not intended to remain here long term; this will be added as a "normal" page of nextstrain.org once some technical hurdles are solved with that site.

### Viz library

We are using our generalised [@nextstrain/evofr-viz library](https://github.com/nextstrain/forecasts-viz) which is packed and
vendored here. To update the library:

1. In the library repo itself run `npm pack` to create a tarball
2. Move the tarball to this folder (`./viz`) so it will be committed, and remove the old one if necessary
3. `npm install <path_to_tarball>`

If this fails to update for some reason then removing `package-lock.json` and reinstalling seems to work.

### Config

The [config file](./src/config.js) defines the variant colors, display names as well as the URLs where the model JSONs are fetched from.

### Static image generation

```
# running from the viz directory
npm run build
node scripts/static-images.js
# images will be in ./figures
```

This is run via the `generate-static-model-viz` GitHub action of this repo