import { variantColors, variantDisplayNames } from "./ncovSpecificSettings";

/** An "empty" data point.
 * Map used instead of object as it's (seemingly) faster + consumes less
 * memory (https://www.zhenghao.io/posts/object-vs-map)
 */
const Point = new Map([
  ['date', undefined],
  ['freq', NaN],
  ['I_smooth', NaN],
  ['I_smooth_y0', NaN], // stacked
  ['I_smooth_y1', NaN], // stacked
  ['r_t', NaN],
]);

const THRESHOLD_FREQ = 0.005; /* half a percent */

/**
 * <returned_Object> ["points"] [location] [ variant ][ dateIdx ] : Point
 *                   ["variants"] : list
 *                   ["dates"] : list
 *                   ["locations"] : list
 *                   ["dateIdx"] : Map (lookup for date string -> idx in dates array)
 *                   ["variantColors"] : Map
 *                   ["variantDisplayNames"] : Map
 */
export const parseModelData = (raw) => {

  const dateIdx = new Map(raw.metadata.dates.map((d, i) => [d, i]));

  const data = new Map([
    ["locations", raw.metadata.location],
    ["variants", raw.metadata.variants],
    ["dates", raw.metadata.dates],
    ["variantColors", variantColors],
    ["variantDisplayNames", variantDisplayNames],
    ["dateIdx", dateIdx],
    ["points", undefined]
  ])

  const points = new Map(
    data.get('locations').map((location) => [
      location,
      new Map(
        data.get('variants').map((variant) => [
          variant,
          raw.metadata.dates.map((date) => {
            const pt = new Map(Point);
            pt.set('date', date);
            return pt;
          })
        ])
      )
    ])
  );

  /* Iterate through each data element & assign to our structure */
  raw.data.forEach((d) => {
    if (d.site==="freq") {
      if (d.ps==="median") {
        points.get(d.location).get(d.variant)[dateIdx.get(d.date)].set('freq', d.value);
      }
    } else if (d.site==="R") {
      if (d.ps==="median") {
        points.get(d.location).get(d.variant)[dateIdx.get(d.date)].set('r_t', d.value);
      }
    }
    else if (d.site==="I_smooth") {
      if (d.ps==="median") {
        points.get(d.location).get(d.variant)[dateIdx.get(d.date)].set('I_smooth', d.value);
      }
    }
  })

  /* Once everything's been added (including frequencies) - iterate over each point & censor certain frequencies */
  let [nanCount, censorCount] = [0, 0];
  for (const variantMap of points.values()) {
    for (const dateList of variantMap.values()) {
      dateList.forEach((point, idx) => {
        if (isNaN(point.get('freq'))) {
          nanCount++;
        } else if (point.get('freq')<THRESHOLD_FREQ) {
          // reset to empty point (including the date)
          dateList[idx] = new Map(Point);
          censorCount++;
        }
      })
    }
  }

  /* create a stack for I_smooth to help with plotting - this could be in the previous set of
  loops but it's here for readability */
  for (const variantMap of points.values()) {
    let runningTotalPerDay = new Array(raw.metadata.dates.length).fill(0);
    for (const dateList of variantMap.values()) {
      dateList.forEach((point, idx) => {
        point.set('I_smooth_y0', runningTotalPerDay[idx]);
        runningTotalPerDay[idx] += point.get('I_smooth') || 0; // I_smooth may be NaN
        point.set('I_smooth_y1', runningTotalPerDay[idx]);
      })
    }
  }

  console.log(`Renewal model data`)
  console.log(`\t${raw.metadata.location.length} locations x ${raw.metadata.variants.length} variants x ${raw.metadata.dates.length} dates`)
  console.log(`\t${censorCount} ensored points + ${nanCount} points missing`);

  data.set("points", points);
  return data;
};
