import React, { useEffect, useState } from "react";
import NavChat from "./NavChat";
import NewNavChat from "./NewNavChat";
import { useChat } from "../../../contexts/ChatContext";

const NavChatList = () => {
    const {chats} = useChat()
    const [currentChats,setCurrentChats] = useState(null);
    

    useEffect(() => {
        if(!chats){
            setCurrentChats(null);
            return
        }
        if (!Array.isArray(chats)){
            return;
        }

        if (currentChats === null){
            const initialChats =  chats.map((chat)=>({...chat,new:false}));
            setCurrentChats(initialChats);
            return;
        }

        const isNewChat = currentChats.length !== chats.length;    
        if (isNewChat) {
            const newChats = chats.map((chat) => ({ ...chat, new: !currentChats.find((c) => c.id === chat.id) }));
            setCurrentChats(newChats);
        }
      }, [chats,currentChats]);


    return (
        <>
            <div className={"navPromptWrapper"}  style={{}}>
                {currentChats&&Array.isArray(currentChats)&&currentChats.map((c, index) => (
                    c.new === true ? (
                        <NewNavChat chat={c} key={`chat_${index}`} />
                    ) : (
                        <NavChat chat={c} key={`chat_${index}`} />
                    )
                ))}
            </div>
        </>
    );
}
export default NavChatList;

