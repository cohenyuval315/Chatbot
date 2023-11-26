import React, { useEffect, useRef, useState } from "react";
import { useChat } from "../../contexts/ChatContext";
import ChatPrompt from "./ChatLog/ChatPrompt";
import BotMessage from "./ChatLog/BotMessage";

const ChatLog = () => {
const {selectedChat,tempItem} = useChat();
const [currentSelectedChat,setCurrentSelectedChat] = useState(null);
const [currentChatLogs,setCurrentChatLogs] = useState(null);
const chatLogRef = useRef(null);

useEffect(()=>{
  // console.log("TEMP:",tempItem)
    if (currentSelectedChat === null || currentSelectedChat.chat_id !== selectedChat.chat_id){
        setCurrentSelectedChat(selectedChat);
        const logs = selectedChat.logs.map((c)=>{
          c.new = false
          return c;
        })
        // console.log(logs);
        setCurrentChatLogs(logs);
        return;
    }
    
    if(tempItem === null){
      setCurrentChatLogs(prev=>[...prev.filter((item)=>item.prompt_id !== -1)]);
    }else{
      setCurrentChatLogs(prev=>[...prev,tempItem]);
    }

    const newLog = selectedChat.logs.length !== [...currentChatLogs.filter((item)=>item.prompt_id !== null)].length
    if(newLog){
        const newLogs = selectedChat.logs.map((log)=>{
        if ([...currentChatLogs.map((item)=>item.prompt_id)].includes(log.prompt_id)){
          log.new = false;
        }else{
          log.new = true;
        }
        return log;
      })
      if(tempItem === null){
        setCurrentChatLogs(newLogs);
      }else{
        setCurrentChatLogs(prev=>[...prev,tempItem]);
      }
      
    }

    

},[selectedChat,tempItem])

useEffect(() => {
    if (chatLogRef.current) {
      chatLogRef.current.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }
    return () => {};
  }, [currentChatLogs]);


  return (
    <div className="chatLogWrapper">
        {currentChatLogs && Array.isArray(currentChatLogs) && currentChatLogs.length > 0 && currentChatLogs.map((log, idx) => {
            return (
            <div ref={chatLogRef} className="chatLog" key={`msg_${idx}`}>
                <ChatPrompt text={log.prompt} />
                <BotMessage chatLogRef={chatLogRef} response={log.response} animate={log.new} />
            </div>
        )})}
    </div>
  );
};

export default ChatLog;
