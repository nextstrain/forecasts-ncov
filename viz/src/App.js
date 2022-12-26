import React from 'react';
import { Container } from './Container.js';
import { useDataFetch } from './dataFetch.js';
import { Panels } from "./Panels.js"
import {Status} from "./Status";

function App() {
  const [modelData, status] = useDataFetch()   
  console.log("Status", Status)
  return (
    <Container>
      {modelData ?
        <Panels modelData={modelData}/> :
        <Status err={status.err}>{status.msg}</Status>
      }
    </Container>
  );
}

export default App;
