import React, {useEffect, useRef} from 'react';
import styled from 'styled-components';
import * as d3 from "d3";

/**
 * A lot of these functions can be broken out into custom hooks / separate files.
 * But for now, this is easier...
 */

const D3Container = styled.div`
  & > div { /* TOOLTIP */
    position: fixed;
    display: none;
    padding: 12px 6px;
    background: #fff;
    border: 1px solid #333;
    pointer-events: none;
  }
`;

const dateFormatter = (dStr) => {
  const date = d3.timeParse("%Y-%m-%d")(dStr);
  if (parseInt(d3.timeFormat("%d")(date), 10)===1) {
    return `${d3.timeFormat("%b")(date)}`;
  }
  return '';
}

const temporalXAxis = (x, sizes) => (g) => g
  .attr("transform", `translate(0,${sizes.height - sizes.margin.bottom})`)
  .call(d3.axisBottom(x).tickSize(0))
  // .call(g => g.select(".domain").remove())
  .selectAll("text")
    .text(dateFormatter)
    // .attr("y", 0)
    // .attr("x", (d) => x(d))
    .attr("dy", "0.6em")
    .attr("transform", "rotate(45)")
    .style("text-anchor", "start")
    .style("font-size", "12px")
    .style("font-family", "Lato, courier")
    .style("fill", "#aaa");

const simpleYAxis = (y, sizes, textFun = (d) => d) => (g) => g
  .attr("transform", `translate(${sizes.margin.left},0)`)
  .call(d3.axisLeft(y).tickSize(0).tickPadding(4))
  // .call(g => g.select(".domain").remove())
  .selectAll("text")
    .text(textFun)
    .style("font-size", "12px")
    .style("font-family", "Lato, courier")
    .style("fill", "#aaa");

const svgSetup = (dom, sizes) => {
  dom.selectAll("*").remove();

  return dom.append("svg")
    .attr("width", sizes.width)
    .attr("height", sizes.height)
    .attr("viewBox", `0 0 ${sizes.width} ${sizes.height}`);
}

const title = (svg, sizes, text) => {
  // top-left so we don't obscure any recent activity
  svg.append("text")
    .text(text)
    .attr("x", sizes.margin.left+5)
    .attr("y", sizes.margin.top) // todo!
    .style("text-anchor", "start")
    .style("dominant-baseline", "hanging")
    .style("font-size", "16px")
    .style("font-family", "Lato, courier")
    .style("fill", "#444");
}

const frequencyPlot = (dom, sizes, location, modelData) => {
  const svg = svgSetup(dom, sizes);

  const x = d3.scalePoint()
    .domain(modelData['dates'])
    .range([sizes.margin.left, sizes.width-sizes.margin.right]);

  svg.append("g")
      .call(temporalXAxis(x, sizes));

  const y = d3.scaleLinear()
    .domain([0, 1])
    .range([sizes.height-sizes.margin.bottom, sizes.margin.top]); // y=0 is @ top. Range is [bottom_y, top_y] which maps 0 to the bottom and 1 to the top (of the graph)
  
  svg.append("g")
    .call(simpleYAxis(y, sizes));

  // Add dots - one group per variant
  Object.entries(modelData.freq[location]).forEach(([variant, points]) => {
    svg.append('g')
      .selectAll("dot")
      .data(points)
      .enter()
      .append("circle")
        .attr("cx", function (d) { return x(d.date); } )
        .attr("cy", function (d) { return y(d.value); } )
        .attr("r", 1.5)
        .style("fill", modelData.cladeColours[variant] ||  modelData.cladeColours.other)
  });

  title(svg, sizes, location)
}


const rtPlot = (dom, sizes, location, modelData) => {
  // todo: y-axis domain depending on data
  // todo: CIs

  const svg = svgSetup(dom, sizes);

  const x = d3.scalePoint()
    .domain(modelData['dates'])
    .range([sizes.margin.left, sizes.width-sizes.margin.right]);

  svg.append("g")
      .call(temporalXAxis(x, sizes));

  const y = d3.scaleLinear()
    .domain([0, 3]) // should be data-driven
    .range([sizes.height-sizes.margin.bottom, sizes.margin.top]); // y=0 is @ top. Range is [bottom_y, top_y] which maps 0 to the bottom and 1 to the top (of the graph)
  
  svg.append("g")
    .call(simpleYAxis(y, sizes));

  /* coloured lines for each variant */
  // line path generator
  const line = d3.line()
    // .defined(i => D[i]) // todo - check for NaN-like values?
    .curve(d3.curveLinear)
    .x((d) => x(d.date))
    .y((d) => y(d.value))

  Object.entries(modelData.r_t[location]).forEach(([variant, points]) => {
    const g = svg.append('g');
    g.append('path')
      .attr("fill", "none")
      .attr("stroke", modelData.cladeColours[variant] ||  modelData.cladeColours.other)
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0.8)
      .attr("d", line(points));
    const finalPt = points[points.length-1]
    g.append("text")
      .text(`${finalPt.value}`)
      .attr("x", x(finalPt.date))
      .attr("y", y(finalPt.value))
      .style("text-anchor", "start")
      .style("alignment-baseline", "baseline")
      .style("font-size", "10px")
      .style("font-family", "Lato, courier")
      .style("fill", modelData.cladeColours[variant] ||  modelData.cladeColours.other)
  });

  /* dashed horizontal line at r_t=1 */
  svg.append('path')
    .attr("fill", "none")
    .attr("stroke", "#444")
    .attr("stroke-width", 1)
    .attr("stroke-opacity", 1)
    .attr("d", `M ${sizes.margin.left} ${y(1.0)} L ${sizes.width-sizes.margin.right} ${y(1.0)}`)
    .style("stroke-dasharray", "4 2")

  title(svg, sizes, location)
}


const stackedCases = (dom, sizes, location, modelData) => {

  if (Object.values(modelData.stackedCases[location]).some((el) => el.length===0)) {
    console.log(`${location} skipped due to empty arrays`)
    return;
  }

  const svg = svgSetup(dom, sizes);

  const x = d3.scalePoint()
    .domain(modelData['dates'])
    .range([sizes.margin.left, sizes.width-sizes.margin.right]);

  svg.append("g")
      .call(temporalXAxis(x, sizes));

  const valuesPerVariant = Object.values(modelData.stackedCases[location]);
  const maxCaseCount = d3.max(valuesPerVariant[valuesPerVariant.length-1].map((d) => d.newCaseTotal))
  const y = d3.scaleLinear()
    .domain([0, maxCaseCount]) // should be data-driven
    .range([sizes.height-sizes.margin.bottom, sizes.margin.top]); // y=0 is @ top. Range is [bottom_y, top_y] which maps 0 to the bottom and 1 to the top (of the graph)
  
  svg.append("g")
    .call(simpleYAxis(y, sizes, d3.format("~s")));

  svg.append('g')
    .selectAll("stakedLayer")
    .data(Object.values(modelData.stackedCases[location]))
    .enter()
    .append("path")
      .style("fill", (d) => modelData.cladeColours[d[0].variant] ||  modelData.cladeColours.other)
      .style("fill-opacity", "0.5")
      .style("stroke", (d) => modelData.cladeColours[d[0].variant] ||  modelData.cladeColours.other)
      .style("stroke-width", 1.5)
      .attr("d", d3.area()
        .x((el) => x(el.date))
        .y0((el) => y(el.previousCaseTotal))
        .y1((el) => y(el.newCaseTotal))
    )
  title(svg, sizes, location)
}


export const SmallMultiple = ({location, graph, sizes, modelData}) => {

  const d3Container = useRef(null);

  console.log("<SmallMultiple/>")
  useEffect(
    () => {
      const dom = d3.select(d3Container.current);

      switch (graph) {
        case 'freq':
          frequencyPlot(dom, sizes, location, modelData);
          break;
        case 'r_t':
          rtPlot(dom, sizes, location, modelData);
          break;
        case 'stackedCases':
          stackedCases(dom, sizes, location, modelData);
          break;
        default:
          console.error(`Unknown graph type ${graph}`)
      }

    },
    [modelData, graph, sizes, location]
  );

  return (
    <D3Container ref={d3Container}/>
  )
}