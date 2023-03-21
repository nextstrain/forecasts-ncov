import { ModelDataProvider, ModelDataStatus, PanelDisplay, useModelData } from 'nextstrain-evofr-viz';
import { config } from "./config";

function App() {

  return (
    <div className="App">
      <ModelDataProvider config={config}>
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
        <ModelDataStatus/>
        <Panels/>
      </ModelDataProvider>
    </div>
  )
}

function Panels() {
  const {modelData} = useModelData();
  if (!modelData) {
    /* not loaded, or an error etc */
    return null;
  }

  return (
    <div id="mainPanelsContainer">
      <h2>Frequencies</h2>
      <div id="frequenciesPanel"> {/* surrounding div(s) used for static-images.js script */}
        <PanelDisplay graphType="frequency"/>
      </div>

      <h2>Growth Advantage</h2>
      <div id="growthAdvantagePanel">
        <PanelDisplay graphType="growthAdvantage"/>
      </div>

      <h2>Cases</h2>
      <div id="smoothedIncidencePanel">
        <PanelDisplay graphType="stackedIncidence" />
      </div>

      <h2>Effective Reproduction Number over time</h2>
      <div id="rtPanel">
        <PanelDisplay graphType="r_t"/>
      </div>
    </div>
  )
}

export default App
