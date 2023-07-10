import { PanelDisplay, useModelData } from '@nextstrain/evofr-viz';
import '@nextstrain/evofr-viz/dist/index.css';
import { mlrCladesConfig, mlrLineagesConfig } from "./config";

function App() {

  const mlrCladesData = useModelData(mlrCladesConfig);
  const mlrLineagesData = useModelData(mlrLineagesConfig);

  return (
    <div className="App">

      <div id="mainPanelsContainer">
        <h2>Clade frequencies over time</h2>
        <p>
          Each line represents the estimated frequency of a particular clade through time.
          Equivalent Pango lineage is given in parenthesis, eg clade 23A (lineage XBB.1.5).
          Results last updated {mlrCladesData?.modelData?.get('updated') || 'loading'}.
        </p>
        <div id="cladeFrequenciesPanel" class="panelDisplay"> {/* surrounding div(s) used for static-images.js script */}
          <PanelDisplay data={mlrCladesData} params={{preset: "frequency"}}/>
        </div>

        <h2>Clade growth advantage</h2>
        <p>
          These plots show the estimated growth advantage for given clades relative to clade
          23A (lineage XBB.1.5). This describes how many more secondary infections a variant causes
          on average relative to clade 23A. Vertical bars show the 95% HPD. The "hierarchical" panel
          shows pooled estimate of growth rates across different regions.
          Results last updated {mlrCladesData?.modelData?.get('updated') || 'loading'}.
        </p>
        <div id="cladeGrowthAdvantagePanel" class="panelDisplay">
          <PanelDisplay data={mlrCladesData} params={{preset: "growthAdvantage"}}/>
        </div>

        <h2>Lineage frequencies over time</h2>
        <p>
          Each line represents the estimated frequency of a particular Pango lineage through time.
          Lineages with fewer than 350 observations are collapsed into parental lineage.
          Results last updated {mlrLineagesData?.modelData?.get('updated') || 'loading'}.
        </p>
        <div id="lineageFrequenciesPanel" class="panelDisplay">
          <PanelDisplay data={mlrLineagesData} params={{preset: "frequency"}}/>
        </div>

        <h2>Lineage growth advantage</h2>
        <p>
          These plots show the estimated growth advantage for given Pango lineages relative to
          lineage XBB.1.5. This describes how many more secondary infections a variant causes
          on average relative to lineage XBB.1.5. Vertical bars show the 95% HPD.
          The "hierarchical" panel shows pooled estimate of growth rates across different regions.
          Results last updated {mlrLineagesData?.modelData?.get('updated') || 'loading'}.
        </p>
        <div id="lineageGrowthAdvantagePanel" class="panelDisplay">
          <PanelDisplay data={mlrLineagesData} params={{preset: "growthAdvantage"}}/>
        </div>

      </div>
    </div>
  )
}

export default App
