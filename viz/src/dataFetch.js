import {useState, useEffect} from 'react';
import renewalJson from "./data/renewal.json"
import {parseModelData} from "./parse.js";


export const useDataFetch = () => {

  const [status, setStatus] = useState("Initialising");
  const [modelData, setModelData] = useState(undefined);

  // todo - fetch the data!!!!!
  useEffect( () => {
    async function fetchAndParse() {
      const renewalData = renewalJson;
      setModelData(parseModelData(renewalData));
      setStatus("ready")
    }
    setStatus("Fetching data (from disk - so you should not see this)...")
    fetchAndParse();

  }, []);


  return [modelData, status]
}