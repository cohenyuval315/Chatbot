
import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import client from '../API/APIClient';


const ChatContext = createContext();

export function useChat() {
  return useContext(ChatContext);
}

export const newChat = {
  "chat_id":null,
  "title":null,
  "log":[]
}

export const introChat = {
  "chat_id":-1,
  "title":null,
  "log":[]
}





export function ChatProvider({ children }) {
  const [chats, setChats] = useState(null);
  const [selectedChat, setSelectedChat] = useState(introChat);
  const [tempItem,setTempItem] = useState(null);
  
  const [loading, setLoading] = useState(true)
  const [selectedChatLoading, setSelectedChatLoading] = useState(false);
  const [selectedChatError, setSelectedChatError] = useState(false);
  const [error, setError] = useState(false);

  const printInterval = 50;

  useEffect(()=>{
    fetchChats().then((data)=>{
      setLoading(false);
    })
  },[])

  const fetchChats = useCallback(async () => {
    try {
      const chatsData = await client.fetchChats()
      const data = chatsData['data']
      setChats(data);
      setError(false);
      return data;
    } catch (error) {
      console.error(error);
      setError(error);
    }
  },[])

  const createNewChat = async (prompt) => {
    try {
      const data = await client.createNewChat(prompt);
      setError(false);
      return data;
    } catch (error){
      setError(error);
    }
  }

  const onChatSelect = async  (item) => {
    try {
      setSelectedChatLoading(true);
      const chat_id = item.chat_id;
      const chatData = await client.getChat(chat_id);
      const data = chatData['data']
      setSelectedChat(data);
      setSelectedChatLoading(false);
      setSelectedChatError(false);
      return chatData;
    } catch (error){
      console.error(error);
      setSelectedChatError(error);
      setSelectedChatLoading(false);
    }
    
  }

  const onNewChatSelect = () => {
    setSelectedChat(newChat);
  }

  const onMessageNewChat = async (prompt) => {
    const item = await createNewChat(prompt);
    const data = item['data'];
    if (item){
      const selected = await onChatSelect(data);
      if (selected){
        const items = await fetchChats();
        if (items){

        }else{
          console.error("could not update chats items");
        }

      }else{
        console.error("could not select new chat");
      }
    }else{
      console.error("could not create new chat");
    }
  }

  const onChatConverse = async (prompt) => {
    setTempItem(null);
    if (selectedChat && selectedChat.chat_id !== null && selectedChat !== -1){
      const updateRes = await client.updateChat(selectedChat.chat_id,prompt);
      const res = await client.getChat(selectedChat.chat_id);
      const chat = res['data']
      setSelectedChat(chat);
    }

  }

  const deleteSelectedChat = async (chat_id) => {
    const res = await client.deleteChat(chat_id);
    if (res['statusCode'] === 200){
      setSelectedChat(newChat)
      await fetchChats()
    }else{

    }
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  const handleInputSubmit = async (prompt) => {
    let res = null;
    if (!selectedChat){
      console.log("handleInputSubmit:Should Not Be Here...")
      return
    }
    setTempItem({
      "prompt_id":null,
      "prompt":prompt
    });
    if(selectedChat.chat_id === null || selectedChat.chat_id === -1){ // Create New Chat
      res = await onMessageNewChat(prompt);
      setTempItem(null);
    }else{
      res =  await onChatConverse(prompt);
    }
    return res;
  }





  return (
    <ChatContext.Provider value={{ 
      printInterval,
      chats,
      selectedChat, 
      loading,
      error,
      selectedChatError,
      selectedChatLoading, 
      tempItem,
      onChatSelect, 
      onNewChatSelect,
      onChatConverse,
      onMessageNewChat,
      handleInputSubmit,
      deleteSelectedChat
       }}>
      {children}
    </ChatContext.Provider>
  );
}