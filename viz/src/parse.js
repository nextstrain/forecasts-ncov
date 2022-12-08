
// following hardcoded for initial simplicity 
const lineageColours = {
  "other": "#737373",
  "BA.2": "#BDBDBD",
  "BA.4": "#447CCD",
  "BA.5": "#5EA9A1",
  "BA.2.12.1": "#8ABB6A",
  "BA.2.75": "#BEBB48",
  "BQ.1": "#E29E39",
  "XBB": "#E2562B"
};

const cladeToLineage = {
  "other": "other",
  "21L (Omicron)": "BA.2",
  "22A (Omicron)": "BA.4",
  "22B (Omicron)": "BA.5",
  "22C (Omicron)": "BA.2.12.1",
  "22D (Omicron)": "BA.2.75",
  "22E (Omicron)": "BQ.1",
  "22F (Omicron)": "XBB",
};

export const parseModelData = (raw) => {
  
  const freq = Object.fromEntries(raw.metadata.location.map((loc) => [
    loc,
    Object.fromEntries(raw.metadata.variants.map((variant) => [
      variant, 
      raw.data.filter((el) => el.location===loc && el.variant===variant && el.ps==="median" && el.site==="freq")
    ]))
  ]))

  // variants in the JSON are nextstrain clades
  const expectedVariants = new Set(Object.keys(cladeToLineage));
  if (!(raw.metadata.variants.length === expectedVariants.size && raw.metadata.variants.every(value => expectedVariants.has(value)))) {
    console.log("New variants / clades! Please update colors. Data has:", new Set(raw.metadata.variants), "but code has", expectedVariants);
  }
  const cladeColours = Object.fromEntries(Object.entries(cladeToLineage).map(([clade, lineage]) => [clade, lineageColours[lineage]]))

  const data = {
    dates: raw.metadata.dates,
    freq,
    locations: raw.metadata.location,
    cladeColours,
    cladeToLineage
  }
  console.log("Parsed model data:", data)

  return data;

};