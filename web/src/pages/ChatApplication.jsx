import React from "react";
import LeftMenu from "../components/LeftMenu/LeftMenu";
import ChatBox from "../components/ChatBox/ChatBox";
import { useChat } from "../contexts/ChatContext";
import LoadingPage from "./LoadingPage";

const ChatApplication = () => {
  const {loading,chatsLoading} = useChat();
  return (
    <>
      {!loading && !chatsLoading ? (      
         <div className="App">        
            <header className="App-header">
            </header>
          <LeftMenu />
          <ChatBox />
        </div>
      ) : <LoadingPage/>}

    </>
  );
};

export default ChatApplication;