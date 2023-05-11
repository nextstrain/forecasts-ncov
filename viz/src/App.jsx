import { PanelDisplay, useModelData } from '@nextstrain/evofr-viz';
import '@nextstrain/evofr-viz/dist/index.css';
import { renewalConfig, mlrConfig } from "./config";

function App() {

  const mlrData = useModelData(mlrConfig);
  const renewalData = useModelData(renewalConfig);

  return (
    <div className="App">
      <h1>Nextstrain SARS-CoV-2 Forecasts</h1>
      <div className="abstract">
        {`The interactive visualisations of evofr modelling data using `}
        <a href="github.com/nextstrain/forecasts-viz/">our visualisation library</a>{`.`}
        <p/>
        {`Currently this page is used to generate static images which are then used within the
        nextstrain.org codebase - please edit that page to update the titles and abstracts.`}
        <p/>
        {`The config ('./src/config.js') defines the variant colors, display names as well as
        the URLs where the model JSONs are fetched from.`}
      </div>

      <div id="mainPanelsContainer">
        <h2>Frequencies (MLR model)</h2>
        <div id="frequenciesPanel"> {/* surrounding div(s) used for static-images.js script */}
          <PanelDisplay data={mlrData} params={{preset: "frequency"}}/>
        </div>

        <h2>Growth Advantage (MLR model)</h2>
        <div id="growthAdvantagePanel">
          <PanelDisplay data={mlrData} params={{preset: "growthAdvantage"}}/>
        </div>

        <h2>Cases (Renewal model)</h2>
        <div id="smoothedIncidencePanel">
          <PanelDisplay data={renewalData} params={{preset: "stackedIncidence"}} />
        </div>

        <h2>Effective Reproduction Number over time (Renewal model)</h2>
        <div id="rtPanel">
          <PanelDisplay data={renewalData} params={{preset: "R_t"}}/>
        </div>
      </div>
    </div>
  )
}

export default App
