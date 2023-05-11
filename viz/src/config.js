
/**
 * Eventually all of these will (hopefully) be part of the
 * JSON itself.
 */

const DEFAULT_ENDPOINT_PREFIX = "https://nextstrain-data.s3.amazonaws.com/files/workflows/forecasts-ncov";
const mlrCladesUrl = `${DEFAULT_ENDPOINT_PREFIX}/gisaid/nextstrain_clades/global/mlr/latest_results.json`;
const mlrLineagesUrl = `${DEFAULT_ENDPOINT_PREFIX}/gisaid/pango_lineages/global/mlr/latest_results.json`;

const variantColors = new Map([
  ["other", "#595959"],
  ["22B (Omicron)", "#A6A6A6"],
  ["22D (Omicron)", "#4D21AD"],
  ["22E (Omicron)", "#4C90C0"],
  ["22F (Omicron)", "#8EBC66"],
  ["23A (Omicron)", "#DEA73C"],
  ["23B (Omicron)", "#DB2823"],
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
