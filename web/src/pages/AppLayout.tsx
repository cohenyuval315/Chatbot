import Chat from './Chat';
import {ChatProvider} from "../context/ChatContext"
function AppLayout() {
  return (
    <div className="App">
      <header className="App-header">
      </header>
      <ChatProvider>
        <Chat/>
      </ChatProvider>
    </div>
  );
}

export default AppLayout;
