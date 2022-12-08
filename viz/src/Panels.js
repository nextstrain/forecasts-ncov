import React from 'react';
import styled from 'styled-components';
import { SmallMultiple } from "./SmallMultiple.js";


export const PanelSectionContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
`;

export const PanelSectionHeaderContainer = styled.div`
  margin: 30px 0px;
`;

const useResponsiveSizing = () => {
  /* following are in pixel coordinates */
  const width = 250;
  const height = 200;
  /* control the spacing around graphs via the margin of each graph */
  const margin = {top: 5, right: 5, bottom: 40, left: 40}
  const fontSize = "10px";

  return {width, height, margin, fontSize};
}

export const Panels = ({modelData}) => {

  const sizes = useResponsiveSizing();

  const graphParams = modelData.locations.map((location) => (
    {location, graph: "freq", sizes}
  ));

  return (
    <div>
      <PanelSectionHeaderContainer>
        {`Modelled variant frequencies per country, split by nextstrain clade`}
      </PanelSectionHeaderContainer>
      <PanelSectionContainer>
        {graphParams.map((param) => (
          <SmallMultiple {...param} key={`${param.graph}_${param.location}`} modelData={modelData}/>
        ))}
      </PanelSectionContainer>
    </div>
  )
}
