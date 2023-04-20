
/**
 * Eventually all of these will (hopefully) be part of the
 * JSON itself.
 */
const DEFAULT_ENDPOINT_PREFIX = "https://nextstrain-data.s3.amazonaws.com/files/workflows/forecasts-ncov/gisaid/nextstrain_clades/global";
const mlrUrl = `${DEFAULT_ENDPOINT_PREFIX}/mlr/latest_results.json`;
const renewalUrl = `${DEFAULT_ENDPOINT_PREFIX}/renewal/latest_results.json`;

const variantColors = new Map([
  ["other", "#737373"],
  ["21L (Omicron)", "#BDBDBD"],
  ["22A (Omicron)", "#7725c6"],
  ["22B (Omicron)", "#447CCD"],
  ["22C (Omicron)", "#5EA9A1"],
  ["22D (Omicron)", "#8ABB6A"],
  ["22E (Omicron)", "#BEBB48"],
  ["22F (Omicron)", "#E29E39"],
  ["23A (Omicron)", "#E2562B"],
  ["23B (Omicron)", "#FF322C"],
]);
const variantDisplayNames = new Map([
  ["other", "other"],
  ["21L (Omicron)", "21L (BA.2)"],
  ["22A (Omicron)", "22A (BA.4)"],
  ["22B (Omicron)", "22B (BA.5)"],
  ["22C (Omicron)", "22C (BA.2.12.1)"],
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