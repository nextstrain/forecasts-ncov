
const DEFAULT_ENDPOINT_PREFIX = "https://nextstrain-data.s3.amazonaws.com/files/workflows/forecasts-ncov/gisaid/nextstrain_clades/global";
export const config = {
  mlrUrl: `${DEFAULT_ENDPOINT_PREFIX}/mlr/latest_results.json`,
  renewalUrl: `${DEFAULT_ENDPOINT_PREFIX}/renewal/latest_results.json`,
  variantColors: new Map([
    ["other", "#737373"],
    ["21L (Omicron)", "#BDBDBD"],
    ["22A (Omicron)", "#447CCD"],
    ["22B (Omicron)", "#5EA9A1"],
    ["22C (Omicron)", "#8ABB6A"],
    ["22D (Omicron)", "#BEBB48"],
    ["22E (Omicron)", "#E29E39"],
    ["22F (Omicron)", "#E2562B"],
    ["23A (Omicron)", "#FF322C"],
  ]),
  variantDisplayNames: new Map([
    ["other", "other"],
    ["21L (Omicron)", "BA.2"],
    ["22A (Omicron)", "BA.4"],
    ["22B (Omicron)", "BA.5"],
    ["22C (Omicron)", "BA.2.12.1"],
    ["22D (Omicron)", "BA.2.75"],
    ["22E (Omicron)", "BQ.1"],
    ["22F (Omicron)", "XBB"],
    ["23A (Omicron)", "XBB.1.5"],
  ])
}