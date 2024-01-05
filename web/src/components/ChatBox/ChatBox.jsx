import React from "react";
import ChatBoxInput from "./ChatInput/ChatInput";
import IntroSection from "./IntroSection";
import {useChat} from '../../contexts/ChatContext'
import NewChat from "./NewChat";
import ChatLog from "./ChatLog";
import ChatHeader from "./ChatHeader/ChatHeader";

const ChatBox = () => {
    const {selectedChat,deleteSelectedChat,selectedModelOption,modelOptions,onModelSelect,dropdownLabelProperty,dropdownValueProperty} = useChat();
    
    return (
        <section className="chatBox">
            {selectedChat && (
            <>
                {selectedChat.chat_id === null ? (<>
                    <ChatHeader title={"New Chat"} initialOption={selectedModelOption} modelOptions={modelOptions} onModelSelect={onModelSelect} dropdownLabelProperty={dropdownLabelProperty}  dropdownValueProperty={dropdownValueProperty}/>
                    <NewChat/>
                </>) : (<>
                    {selectedChat.chat_id === -1 ? (<>
                        <ChatHeader title={"Introduction"} initialOption={selectedModelOption} modelOptions={modelOptions} onModelSelect={onModelSelect} dropdownLabelProperty={dropdownLabelProperty}  dropdownValueProperty={dropdownValueProperty}/>
                        <IntroSection/>
                    </>) : (<>
                        <ChatHeader title={selectedChat.title} initialOption={selectedModelOption} onDelete={()=>deleteSelectedChat(selectedChat.chat_id)} modelOptions={modelOptions} onModelSelect={onModelSelect} dropdownLabelProperty={dropdownLabelProperty}  dropdownValueProperty={dropdownValueProperty}/>
                        <ChatLog/>
                    </>)}
                </>)}
            </>
            )}
            <ChatBoxInput />
        </section>
    )



};



export default ChatBox;
