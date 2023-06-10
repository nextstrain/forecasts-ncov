
/**
 * Eventually all of these will (hopefully) be part of the
 * JSON itself.
 */

const DEFAULT_ENDPOINT_PREFIX = "https://nextstrain-data.s3.amazonaws.com/files/workflows/forecasts-ncov";
const mlrCladesUrl = `${DEFAULT_ENDPOINT_PREFIX}/gisaid/nextstrain_clades/global/mlr/latest_results.json`;
const mlrLineagesUrl = `${DEFAULT_ENDPOINT_PREFIX}/gisaid/pango_lineages/global/mlr/latest_results.json`;

const variantColors = new Map([
  ["other", "#595959"],
  ["22B (Omicron)", "#416DCE"],
  ["22D (Omicron)", "#59A3AA"],
  ["22E (Omicron)", "#84BA6F"],
  ["22F (Omicron)", "#BBBC49"],
  ["23A (Omicron)", "#E29D39"],
  ["23B (Omicron)", "#E1502A"],
]);
const variantDisplayNames = new Map([
  ["other", "other"],
  ["22B (Omicron)", "22B (BA.5)"],
  ["22D (Omicron)", "22D (BA.2.75)"],
  ["22E (Omicron)", "22E (BQ.1)"],
  ["22F (Omicron)", "22F (XBB)"],
  ["23A (Omicron)", "23A (XBB.1.5)"],
  ["23B (Omicron)", "23B (XBB.1.16)"],
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
