import {useState, useEffect} from 'react';
import {parseModelData} from "./parse.js";

const DEFAULT_ENDPOINT = "https://nextstrain-data.s3.amazonaws.com/files/workflows/forecasts-ncov/trial/2022-12-18_results.json";

export const useDataFetch = () => {
  const [status, setStatus] = useState("Initialising");
  const [modelData, setModelData] = useState(undefined);

  // todo - fetch the data!!!!!
  useEffect( () => {
    let renewalJson;

    if (process.env.REACT_APP_MODEL_ENDPOINT === "local") {
      renewalJson = new Promise((resolve) => {
        resolve(require("./data/renewal.json"))
      });
    } else {
      const endpoint = process.env.REACT_APP_MODEL_ENDPOINT || DEFAULT_ENDPOINT;
      renewalJson = fetch(endpoint)
        .then((res) => res.json())
    }
    async function fetchAndParse() {
      const renewalData = await renewalJson;
      setModelData(parseModelData(renewalData));
      setStatus("ready")
    }
    setStatus("Fetching data...")
    fetchAndParse();

  }, []);


  return [modelData, status]
}