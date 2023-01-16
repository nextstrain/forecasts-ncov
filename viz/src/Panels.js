import React from 'react';
import {PanelDisplay, useModelData} from 'nextstrain-forecasts-viz';
import {PanelSectionHeaderContainer, PanelAbstract} from "./Styles.js";

export const Panels = () => {

  const {modelData} = useModelData();
  if (!modelData) {
    /* not loaded, or an error etc */
    return null;
  }
  
  return (
    <div id="mainPanelsContainer" >

      <PanelSectionHeaderContainer>
        {`Estimated Variant Frequencies over time`}
      </PanelSectionHeaderContainer>
      <PanelAbstract>
        {`These estimates are derived from sequence count data using a multinomial logistic regression model.`}
      </PanelAbstract>

      <PanelDisplay graphType="freq"/>

      <PanelSectionHeaderContainer>
        {`Growth Advantage`}
      </PanelSectionHeaderContainer>
      <PanelAbstract>
        {`
          These plots show the estimated growth advantage for given variants relative to ${modelData.get("variantDisplayNames").get(modelData.get("pivot")) || "baseline"}.
          This is an estimate of how many more secondary infections this variant causes on average compared the baseline variant as estimated but the multinomial logistic regression model.
          Vertical bars show the 95% HPD.
        `}
      </PanelAbstract>
      <PanelDisplay graphType="ga"/>

      <PanelSectionHeaderContainer>
        {`Estimated Cases over time`}
      </PanelSectionHeaderContainer>
      <PanelAbstract>
        {`As estimated by the variant renewal model.
        These estimates are smoothed to deal with daily reporting noise and weekend effects present in case data.`}
      </PanelAbstract>
      <PanelDisplay graphType="stackedIncidence"/>


      <PanelSectionHeaderContainer>
        {`Estimated effective reproduction number over time`}
      </PanelSectionHeaderContainer>
      <PanelAbstract>
        {`This is an estimate of the average number of secondary infections expected to be caused by an individual infected with a given variant as estimated by the variant renewal model.
        In general, we expect the variant to be growing if this number is greater than 1.`}
      </PanelAbstract>
      <PanelDisplay graphType="r_t"/>

    </div>
  )
}
