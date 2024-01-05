
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
  
  const [chatsLoading, setChatsLoading] = useState(true)
  const [loading, setLoading] = useState(true)
  const [selectedChatLoading, setSelectedChatLoading] = useState(false);
  const [selectedChatError, setSelectedChatError] = useState(false);
  const [error, setError] = useState(false);

  const [modelOptions,setModelOptions] = useState(null);
  const [selectedModelOption,setSelectedModelOption] = useState(null);

  const printInterval = 50;
  const dropdownLabelProperty = "model_name";
  const dropdownValueProperty = "model_key";


  const fetchModelOptions = useCallback(async () => {
    try {
      const data = await client.getModelsData();
      const modelsData = data
      const dropdownOptions = modelsData;
      setModelOptions(dropdownOptions);
      setSelectedModelOption(dropdownOptions[0]);  
      setError(false);
      return data;
    } catch (error){
      setError(error);
    }
  },[])


  const fetchChats = useCallback(async () => {
    try {
      const data = await client.getChats()
      setChats(data);
      setError(false);
      return data;
    } catch (error) {
      console.error(error);
      setError(error);
    }
  },[])


  useEffect(()=>{
        
    const fetchData = async () => {
      await fetchModelOptions().then((data)=>{
        setLoading(false);
      })      
      await fetchChats().then((data)=>{
        setChatsLoading(false);
      })

      
      // try {
      //   await Promise.all([fetchModelOptions(), fetchChats()]);
      //   setLoading(false);
      // } catch (error) {
      //   console.error('Error fetching data:', error);
      // }
    };

    fetchData();
    

  }, [fetchModelOptions, fetchChats]);



  const onModelSelect = (modelOption) => {
    setSelectedModelOption(modelOption);
  }


  const createNewChat = async (prompt) => {
    try {
      const data = await client.createNewChat(prompt,selectedModelOption['model_name']);
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
      const data = chatData;
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
    const item = await createNewChat(prompt,selectedModelOption['model_name']);
    const data = item;
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
    if (selectedChat && selectedChat.chat_id !== null && selectedChat !== -1){
      await client.updateChat(selectedChat.chat_id,prompt,selectedModelOption['model_name']);
      const res = await client.getChat(selectedChat.chat_id);
      const chat = res;
      setTempItem(null);
      setSelectedChat(chat);
    }

  }

  const deleteSelectedChat = async (chat_id) => {
    await client.deleteChat(chat_id);
    setSelectedChat(newChat)
    await fetchChats()
  }

  const handleInputSubmit = async (prompt) => {
    let res = null;
    if (!selectedChat){
      console.log("handleInputSubmit:Should Not Be Here...")
      return
    }
    const temp = {
      "prompt_id":null,
      "prompt":prompt
    }
    setTempItem(temp);
    if(selectedChat.chat_id === null || selectedChat.chat_id === -1){ // Create New Chat
      res = await onMessageNewChat(prompt);
     
    }else{
      res =  await onChatConverse(prompt);
    }
    return res;
  }



  

  return (
    <ChatContext.Provider value={{ 
      dropdownLabelProperty,
      dropdownValueProperty,
      selectedModelOption,
      printInterval,
      chats,
      selectedChat, 
      loading,
      chatsLoading,
      error,
      selectedChatError,
      selectedChatLoading, 
      tempItem,
      modelOptions,
      onModelSelect,
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