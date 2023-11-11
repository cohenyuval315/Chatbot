
import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import client from '../API/APIClient';


const ChatContext = createContext();

export function useChat() {
  return useContext(ChatContext);
}

export const newChat = {
  "id":null,
  "title":null,
  "log":[]
}



export function ChatProvider({ children }) {
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(newChat);
  const [inputDisable, setInputDisable] = useState(false);
  const [error, setError] = useState(false);
  const [responseFromAPI,setReponseFromAPI] = useState(false);
  const [botResponse, setBotResponse] = useState(null);
  const [showIntro, setShowIntro] = useState(true);
  const [loading, setLoading] = useState(true)

  const printInterval = 50;



  const fetchChats = useCallback(async () => {
    try {
      const chatsData = await client.fetchChats()
      setChats(chatsData);
      setError(false);
    } catch (error) {
      console.error(error);
      setError(error);
    }
  },[])

  useEffect(()=>{
    fetchChats().then(()=>{
      setLoading(false);
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])


  const finishIntro = () => {
    if(showIntro === true){
      setShowIntro(false);
    }
  }

  const onChatSelect = (title) => {
    console.debug("on chat select")
    if(!responseFromAPI){
      setInputDisable(false);
      const item = chats.filter((chat)=>chat.title === title);
      if (item.length === 1){
        const sc = item[0];
        console.debug("on select ,selected chat:",sc)
        setSelectedChat(sc)
      }else{
        console.error("cant find selected chat: ",title)
      }
    }
    finishIntro();
  }

  const onChatNew = () => {
    console.debug("on chat new")
    if(!responseFromAPI && selectedChat.id !== null){
      setSelectedChat(newChat);
      setBotResponse(null);
      setInputDisable(false);
    }
    finishIntro();
  }

  const addNewChat = (chatId,title,initialPrompt) => {
    console.debug("add new chat")
    if(selectedChat.id !== null){
      return;
    }
    const newUpdatedChat = {
      id:chatId,
      title:title,
      log:[initialPrompt]
    }
    setChats([newUpdatedChat,...chats])
    setSelectedChat(newUpdatedChat);
  }

  useEffect(() => {
    if(botResponse && !error){
      updateSelectedChat(botResponse)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [botResponse])


  const updateSelectedChat = (newChat) => {
    const updatedLog = newChat.id === -1 ? [...selectedChat.log,newChat] : selectedChat.log.map((chat)=>{
      if(chat.id === -1){
        return newChat;
      }
      return chat;
    });
    const updatedChat = {
      id:selectedChat.id,
      title:selectedChat.title,
      log: updatedLog
    }          
    setSelectedChat(updatedChat);
    const updatedChats = chats.map((item)=>{
      return item.id === selectedChat.id ? updatedChat : item;
    })
    setChats(updatedChats);
    setBotResponse(null);
    setInputDisable(false);
  }

  const onChatConverse = async (prompt) => {
    console.debug("chat converse")
    if (!responseFromAPI) {
      try {

        setReponseFromAPI(true);
        //setInputDisable(true);
        const initialPrompt = {
          id:-1,
          prompt: prompt
        }
        setBotResponse(
          initialPrompt
        );
        const res = await client.converse(selectedChat,prompt);
        const chatId = res.id;
        const title = res.title;
        const response = res.data;
        setReponseFromAPI(false);
        setError(false);
        if(selectedChat.id === null){
          addNewChat(chatId,title,initialPrompt);
        }
        setBotResponse(response);
      } catch (err) {
        setError(err);
        console.log(err);
      }finally{
        console.debug(selectedChat);
      }
    }
  }


  const regenerateMessage = async () => {

  }


  return (
    <ChatContext.Provider value={{ 
      chats, 
      loading,
      error,
      inputDisable,
      selectedChat, 
      onChatSelect, 
      responseFromAPI,
      onChatNew,
      printInterval,
      regenerateMessage,
      showIntro,
      finishIntro,
      onChatConverse }}>
      {children}
    </ChatContext.Provider>
  );
}