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

const frequencyPlot = (dom, sizes, location, modelData) => {
  const {width, height, margin} = sizes;
  dom.selectAll("*").remove();

  const svg = dom.append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", `0 0 ${width} ${height}`);

  const x = d3.scalePoint()
    .domain(modelData['dates'])
    .range([margin.left, width-margin.right]);

  const xAxis = (g) => g
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x).tickSize(0))
    // .call(g => g.select(".domain").remove())
    .selectAll("text")
      .text((d, i) => i%20 ? '' : d)
      // .attr("y", 0)
      // .attr("x", (d) => x(d))
      .attr("dy", "0.6em")
      .attr("transform", "rotate(45)")
      .style("text-anchor", "start")
      .style("font-size", "12px")
      .style("font-family", "Lato, courier")
      .style("fill", "#aaa");

  svg.append("g")
      .call(xAxis);

  const y = d3.scaleLinear()
    .domain([0, 1])
    .range([height-margin.bottom, margin.top]); // y=0 is @ top. Range is [bottom_y, top_y] which maps 0 to the bottom and 1 to the top (of the graph)
  
  const yAxis = (g) => g
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).tickSize(0).tickPadding(4))
    // .call(g => g.select(".domain").remove())
    .selectAll("text")
      .text((d) => d)
      .style("font-size", "12px")
      .style("font-family", "Lato, courier")
      .style("fill", "#aaa");
  
  svg.append("g")
    .call(yAxis);

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

  svg.append("text")
    .text(`${location}`)
    .attr("x", width-margin.right)
    .attr("y", margin.top) // todo!
    .style("text-anchor", "end")
    .style("dominant-baseline", "hanging")
    .style("font-size", "16px")
    .style("font-family", "Lato, courier")
    .style("fill", "#aaa");

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