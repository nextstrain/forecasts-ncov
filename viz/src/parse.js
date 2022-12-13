
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
  
  /* frequencies: "freq" → location → variant (clade) → frequencyValue */
  const freq = Object.fromEntries(raw.metadata.location.map((loc) => [
    loc,
    Object.fromEntries(raw.metadata.variants.map((variant) => [
      variant, 
      raw.data.filter((el) => el.location===loc && el.variant===variant && el.ps==="median" && el.site==="freq")
    ]))
  ]))

  /* TODO - we censor data which is based on few data points! */
  /* TODO - we're drawing a line through these, can we guarantee they're date-sorted? */
  /* frequencies: "r_t" → location → variant (clade) → r_tValue */
  const r_t = Object.fromEntries(raw.metadata.location.map((loc) => [
    loc,
    Object.fromEntries(raw.metadata.variants.map((variant) => [
      variant, 
      raw.data.filter((el) => el.location===loc && el.variant===variant && el.ps==="median" && el.site==="R")
    ]))
  ]))

  /* stacked incidence vis I_smooth */

  const stackedIncidence = Object.fromEntries(raw.metadata.location.map((loc) => [
    loc,
    Object.fromEntries(raw.metadata.variants.map((variant) => [variant, []]))
  ]));
  const incidenceKeyed = Object.fromEntries(raw.metadata.location.map((loc) => [
    loc,
    Object.fromEntries(raw.metadata.variants.map((variant) => [variant, {}]))
  ]));
  raw.data.filter((el) => el.ps==="median" && el.site==="I_smooth").forEach((el) => {
    incidenceKeyed[el.location][el.variant][el.date] = parseInt(el.value, 10);
  })

  raw.metadata.location.forEach((loc) => {
    const datesToIgnore = new Set();
    let previousIncidence = {} // per day
    raw.metadata.variants.forEach((variant) => {
      raw.metadata.dates.forEach((date) => {
        const pv = parseInt(previousIncidence[date] || 0, 10);
        const newIncidence = parseInt(pv + incidenceKeyed[loc][variant][date]);
        if (isNaN(newIncidence)) {
          // console.log(`[debug] ${loc} ${variant} ${date} ps=median site=I_smooth doesn't exist!`)
          datesToIgnore.add(date)
        }
        // update previous incidence to the new incidence
        previousIncidence[date] = newIncidence;
        // store this data point, which will form a slice of area in the stacked graph
        if (previousIncidence === newIncidence) {
          return;
        }
        stackedIncidence[loc][variant].push({
          date: date,
          variant,
          previousIncidence: pv,
          newIncidence
        })
      })
    })
    if (datesToIgnore.size>0) {
      console.error(`I_smooth: Ignoring ${[...datesToIgnore]} for ${loc}`)
      raw.metadata.variants.forEach((variant) => {
        stackedIncidence[loc][variant] = stackedIncidence[loc][variant].filter((el) => !datesToIgnore.has(el.date))
      });
    }
  })

  // variants in the JSON are nextstrain clades
  const expectedVariants = new Set(Object.keys(cladeToLineage));
  if (!(raw.metadata.variants.length === expectedVariants.size && raw.metadata.variants.every(value => expectedVariants.has(value)))) {
    console.error("New variants / clades! Please update colors. Data has:", new Set(raw.metadata.variants), "but code has", expectedVariants);
  }
  const cladeColours = Object.fromEntries(Object.entries(cladeToLineage).map(([clade, lineage]) => [clade, lineageColours[lineage]]))

  const data = {
    variants: raw.metadata.variants,
    dates: raw.metadata.dates,
    freq,
    locations: raw.metadata.location,
    cladeColours,
    cladeToLineage,
    r_t,
    stackedIncidence
  }
  console.log("[debugging] Parsed model data:", data)

  return data;

};
