import {useState, useEffect} from 'react';
import renewalJson from "./data/renewal.json"
import {parseModelData} from "./parse.js";
import caseCounts from "./data/caseCounts.json";


export const useDataFetch = () => {

  const [status, setStatus] = useState("Initialising");
  const [modelData, setModelData] = useState(undefined);

  // todo - fetch the data!!!!!
  useEffect( () => {
    async function fetchAndParse() {
      const renewalData = renewalJson;

      /* cases = <location> -> <dateString> -> integer */
      const cases = Object.fromEntries(
        [...new Set(caseCounts.map((o) => o.location))].map((loc) => [loc, {}])
      );
      caseCounts.forEach((o) => {
        cases[o.location][o.date] = o.cases;
      });
  
      setModelData(parseModelData(renewalData, cases));
      setStatus("ready")
    }
    setStatus("Fetching data (from disk - so you should not see this)...")
    fetchAndParse();

  }, []);


  return [modelData, status]
}