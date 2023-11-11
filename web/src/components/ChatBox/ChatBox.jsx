import React, { useEffect, useRef } from "react";
import ChatBoxInput from "./ChatBoxInput";
import IntroSection from "./IntroSection";
import ChatPrompt from "./ChatPrompt";
import {useChat} from '../../context/ChatContext'
import NewChat from "./NewChat";
import BotMessage from "./BotMessage";

const ChatBox = (props) => {
    const {selectedChat,showIntro} = useChat();
    const chatLogRef = useRef(null);

    useEffect(() => {
        if (chatLogRef.current) {
          chatLogRef.current.scrollIntoView({
            behavior: "smooth",
            block: "end",
          });
        }
        return () => {};
      }, []);

    return (
        <section className="chatBox">
            {selectedChat.title}
            {selectedChat.log.length > 0 ? (
                <div className="chatLogWrapper">
                    {selectedChat.log.length > 0 &&
                    selectedChat.log.map((chat, idx) => {
                        return (
                        <div
                        className="chatLog"
                        key={`msg_${idx}`}
                        ref={chatLogRef}
                        >
                            <ChatPrompt text={chat.prompt} />
                            <BotMessage chatLogRef={chatLogRef} response={chat.response} animate={selectedChat.log.length - 1 === idx} />

                        </div>
                        
                    )})}
                </div>
            ) : (
                <>
                {showIntro?<IntroSection/>:<NewChat/>}
                </>
            )}
            <ChatBoxInput />
        </section>
    );




};



export default ChatBox;
