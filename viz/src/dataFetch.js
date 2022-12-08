import {useState, useEffect} from 'react';
import renewalJson from "./data/renewal.json"
import {parseModelData} from "./parse.js";


export const useDataFetch = () => {

  const [status, setStatus] = useState("Initialising");
  const [modelData, setModelData] = useState(undefined);

  // todo - fetch the data!!!!!
  useEffect( () => {
    setStatus("Fetching data (from disk - so you should not see this)...")
    const data = renewalJson;
    setModelData(parseModelData(data));
    setStatus("ready")
  }, []);


  return [modelData, status]
}