import {useState, useEffect} from 'react';
import {parseModelData} from "./parse.js";

const DEFAULT_ENDPOINT = "https://nextstrain-data.s3.amazonaws.com/files/workflows/forecasts-ncov/trial/2022-12-18_results.json";

export const useDataFetch = () => {
  const [status, setStatus] = useState("Initialising");
  const [modelData, setModelData] = useState(undefined);

  useEffect( () => {
    const endpoint = process.env.REACT_APP_MODEL_ENDPOINT || DEFAULT_ENDPOINT;
    const renewalJson = fetch(endpoint)
      .then((res) => res.json())

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