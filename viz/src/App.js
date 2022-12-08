import React from 'react';
import { Container } from './Container.js';
import { useDataFetch } from './dataFetch.js';
import { Panels } from "./Panels.js"

function App() {
  const [modelData, status] = useDataFetch()   

  return (
    <Container>
      {status==="ready" ?
        <Panels modelData={modelData}/> :
        <div>{`Status: ${status}`}</div>
      }
    </Container>
  );
}

export default App;
