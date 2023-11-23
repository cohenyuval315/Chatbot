import React, { useEffect, useRef } from "react";
import ChatBoxInput from "./ChatInput/ChatInput";
import IntroSection from "./IntroSection";
import {useChat} from '../../contexts/ChatContext'
import NewChat from "./NewChat";
import ChatLog from "./ChatLog";
import ChatHeader from "./ChatHeader/ChatHeader";

const ChatBox = () => {
    const {selectedChat,deleteSelectedChat} = useChat();
    
    return (
        <section className="chatBox">
            {selectedChat && (
            <>
                {selectedChat.chat_id === null ? (<>
                    <ChatHeader title={"New Chat"}/>
                    <NewChat/>
                </>) : (<>
                    {selectedChat.chat_id === -1 ? (<>
                        <ChatHeader title={"Introduction"}/>
                        <IntroSection/>
                    </>) : (<>
                        <ChatHeader title={selectedChat.title} onDelete={()=>deleteSelectedChat(selectedChat.chat_id)}/>
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
