import React from 'react';
import './App.css';
import {ChatProvider} from "./contexts/ChatContext";
import ChatApplication from './pages/ChatApplication';

function App() {
  
  return (
    <div className="">
      {/* <header className="App-header">
      </header> */}
      <ChatProvider>
        <ChatApplication/>
      </ChatProvider>
    </div>
  );
}

export default App;
