
import React, { createContext, useCallback, useContext, useEffect,useReducer,  useState } from 'react';
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

function chatsReducer(state,action){
  switch (action.type){
    case 'set':{
      return action.data
    }
    case 'add':{
      return [action.chat,...state]
    }
    case 'update':{
      return state.map((item)=>{
          if(item.chat_id === action.chat.chat_id){
            return action.chat;
          }
          return item;
        });
    }
    case 'delete':{
      return state.filter((item)=>item.chat_id !== action.chat_id);
    }
    default :{
      break;
    }
  }
} 



export function ChatProvider({ children }) {
  const [chats,dispatch] = useReducer(chatsReducer,null);
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

  const setChatsData = async (data) => {

    dispatch({
      type:'set',
      data:data
    })
  }

  const fetchChats = useCallback(async () => {
    try {
      const data = await client.getChats()
      setChatsData(data);
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
    };

    fetchData();
  }, []);


  const onModelSelect = (modelOption) => {
    setSelectedModelOption(modelOption);
  }

  const createNewChat = async (prompt) => {
    try {
      setSelectedChatLoading(true);
      const data = await client.createNewChat(prompt,selectedModelOption['model_name']);
      setSelectedChatLoading(false);
      setError(false);
      return data;
    } catch (error){
      setError(error);
    }
  }

  const deleteChat = async () => {
    if(selectedChat.chat_id !== null && selectedChat.chat_id !== -1){
      dispatch({
        type:'delete',
        chat_id:selectedChat.chat_id
      })
      setSelectedChat(newChat)
      await client.deleteChat(selectedChat.chat_id);
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

    if (item){
      dispatch({
        type:'add',
        chat:item
      })
      const selected = await onChatSelect(item);
      if (selected){

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

  const handleInputSubmit = async (prompt) => {
    let res = null;
    if (!selectedChat){
      console.error("handleInputSubmit:Should Not Be Here...")
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
      deleteChat
       }}>
      {children}
    </ChatContext.Provider>
  );
}