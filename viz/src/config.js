
/**
 * Eventually all of these will (hopefully) be part of the
 * JSON itself.
 */

const DEFAULT_ENDPOINT_PREFIX = "https://nextstrain-data.s3.amazonaws.com/files/workflows/forecasts-ncov";
const mlrCladesUrl = `${DEFAULT_ENDPOINT_PREFIX}/gisaid/nextstrain_clades/global/mlr/latest_results.json`;
const mlrLineagesUrl = `${DEFAULT_ENDPOINT_PREFIX}/gisaid/pango_lineages/global/mlr/latest_results.json`;

const variantColors = new Map([
  ["other", "#777777"],
  ["22B",   "#999999"],
  ["22D",   "#AAAAAA"],
  ["22E",   "#CCCCCC"],
  ["22F",   "#3F63CF"],
  ["23A",   "#529AB6"],
  ["23B",   "#75B681"],
  ["23C",   "#A6BE55"],
  ["23D",   "#D4B13F"],
  ["23E",   "#E68133"],
  ["23F",   "#DC2F24"]
]);
const variantDisplayNames = new Map([
  ["other", "other"],
  ["22B",   "22B (BA.5)"],
  ["22D",   "22D (BA.2.75)"],
  ["22E",   "22E (BQ.1)"],
  ["22F",   "22F (XBB)"],
  ["23A",   "23A (XBB.1.5)"],
  ["23B",   "23B (XBB.1.16)"],
  ["23C",   "23C (CH.1.1)"],
  ["23D",   "23D (XBB.1.9)"],
  ["23E",   "23E (XBB.2.3)"],
  ["23F",   "23F (EG.5.1)"]
]);

export const mlrCladesConfig = {
  modelName: "mlr_clades",
  modelUrl: mlrCladesUrl,
  sites: undefined, // can restrict the sites parsed from the JSON
  variantColors,
  variantDisplayNames
};

export const mlrLineagesConfig = {
  modelName: "mlr_lineages",
  modelUrl: mlrLineagesUrl,
  sites: undefined, // can restrict the sites parsed from the JSON
};
