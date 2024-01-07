import React from "react";
import ChatBoxInput from "./ChatInput/ChatInput";
import IntroSection from "./IntroSection";
import {useChat} from '../../contexts/ChatContext'
import NewChat from "./NewChat";
import ChatLog from "./ChatLog";
import ChatHeader from "./ChatHeader/ChatHeader";
import ChatLoading from "./ChatLoading";

const ChatBox = () => {
    const {
        selectedChat,
        selectedChatLoading,
        deleteSelectedChat,
        } = useChat();
    
    
    return (
        <section className="chatBox">
            {selectedChat && (
            <>
                {selectedChatLoading ? (<ChatLoading />) : (
                    <>
                        {selectedChat.chat_id === null ? (<>
                            <ChatHeader  title={"New Chat"} />
                            <NewChat/>
                        </>) : (<>
                            {selectedChat.chat_id === -1 ? (<>
                                <ChatHeader title={"Introduction"} />
                                <IntroSection/>
                            </>) : (<>
                                    <ChatHeader 
                                        title={selectedChat.title} 
                                        onDelete={()=>deleteSelectedChat(selectedChat.chat_id)} />
                                    <ChatLog/>
                            </>)}
                        </>)}
                    </>
                )}

            </>
            )}
            <ChatBoxInput />
        </section>
    )



};



export default ChatBox;
