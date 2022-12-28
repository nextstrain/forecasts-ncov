import React, {useRef} from 'react';
import styled from 'styled-components';
import { SmallMultiple } from "./SmallMultiple.js";
import {useLegend} from "./Legend.js"

const WINDOW_WIDTH_FOR_SIDEBAR_LEGEND = 1200;

const Container = styled.div`
  @media screen and (min-width: ${WINDOW_WIDTH_FOR_SIDEBAR_LEGEND}px) {
    margin-right: 100px; // + the 100px from <App> Container
  }
`;

const PanelSectionContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
`;

const PanelSectionHeaderContainer = styled.div`
  margin-bottom: 30px;
  margin-top: 50px;
`;

const LegendContainer = styled.div`
  /* border: solid red; */
  display: flex;
  
  /* legend-inline styles (which will be overridden by a media query if necessary) */
  position: block;
  flex-wrap: wrap;
  flex-direction: row;
  margin: 10px 0px;
  & > div {
    padding-right: 10px;
  }

  @media screen and (min-width: ${WINDOW_WIDTH_FOR_SIDEBAR_LEGEND}px) {
    position: fixed;
    right: 0px;
    max-width: 200px;
    min-width: 200px;
    flex-wrap: nowrap;
    flex-direction: column;
    & > div {
      padding-right: 0px;
    }
  }

`;

const useResponsiveSizing = () => {
  /* following are in pixel coordinates */
  const width = 250;
  const height = 200;
  /* control the spacing around graphs via the margin of each graph */
  const margin = {top: 5, right: 30, bottom: 40, left: 30}
  const fontSize = "10px";

  return {width, height, margin, fontSize};
}

export const Panels = ({modelData, sidebar}) => {

  const sizes = useResponsiveSizing();
  const legendContainer = useRef(null);
  useLegend(legendContainer, modelData); // renders the legend

  return (
    <Container id="mainPanelsContainer" >

      <PanelSectionHeaderContainer>
        {`Modelled variant frequencies per country, split by nextstrain clade`}
      </PanelSectionHeaderContainer>

      {/* To do - the only appears once, however the intention is that on small screens
      it should appear above _every_ <PanelSectionContainer/> */}
      <LegendContainer id="legend" ref={legendContainer}/>

      <PanelSectionContainer id="frequenciesPanel">
        {modelData.get('locations')
          .map((location) => ({location, graph: "freq", sizes}))
          .map((param) => (
            <SmallMultiple {...param} key={`${param.graph}_${param.location}`} modelData={modelData}/>
          ))
        }
      </PanelSectionContainer>

      <PanelSectionHeaderContainer>
        {`Modelled R_t per country, split by nextstrain clade`}
      </PanelSectionHeaderContainer>
      <PanelSectionContainer id="rtPanel">
      {modelData.get('locations')
          .map((location) => ({location, graph: "r_t", sizes}))
          .map((param) => (
            <SmallMultiple {...param} key={`${param.graph}_${param.location}`} modelData={modelData}/>
          ))
        }
      </PanelSectionContainer>

      <PanelSectionHeaderContainer>
        {`Smoothed Incidence`}
      </PanelSectionHeaderContainer>
      <PanelSectionContainer id="smoothedIncidencePanel">
        {modelData.get('locations')
          .map((location) => ({location, graph: "stackedIncidence", sizes}))
          .map((param) => (
            <SmallMultiple {...param} key={`${param.graph}_${param.location}`} modelData={modelData}/>
          ))
        }
      </PanelSectionContainer>

      <PanelSectionHeaderContainer>
        {`Growth Advantage`}
      </PanelSectionHeaderContainer>
      <PanelSectionContainer id="smoothedIncidencePanel">
        {modelData.get('locations')
          .map((location) => ({location, graph: "ga", sizes}))
          .map((param) => (
            <SmallMultiple {...param} key={`${param.graph}_${param.location}`} modelData={modelData}/>
          ))
        }
      </PanelSectionContainer>

    </Container>
  )
}
