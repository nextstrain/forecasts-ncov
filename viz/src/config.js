
/**
 * Eventually all of these will (hopefully) be part of the
 * JSON itself.
 */
const DEFAULT_ENDPOINT_PREFIX = "https://nextstrain-data.s3.amazonaws.com/files/workflows/forecasts-ncov/gisaid/nextstrain_clades/global";
const mlrUrl = `${DEFAULT_ENDPOINT_PREFIX}/mlr/latest_results.json`;
const renewalUrl = `${DEFAULT_ENDPOINT_PREFIX}/renewal/latest_results.json`;

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

export const mlrConfig = {
  modelName: "MLR",
  modelUrl: mlrUrl,
  sites: undefined, // can restrict the sites parsed from the JSON
  variantColors,
  variantDisplayNames
};
export const renewalConfig = {
  modelName: "Renewal",
  modelUrl: renewalUrl,
  sites: undefined, // can restrict the sites parsed from the JSON
  variantColors,
  variantDisplayNames
};
