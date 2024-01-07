import React, { useEffect, useState,useRef } from "react";
import NavChat from "./NavChat";
import NewNavChat from "./NewNavChat";
import { useChat } from "../../../contexts/ChatContext";

const NavChatList = () => {
    const {chats} = useChat()
    const [newChatID,setNewChatID] = useState(null)
    
    const prevChats = useRef(chats);

    useEffect(()=>{
        if(chats === null){
            return;
        }
        if(chats !== null && prevChats.current !== null){
            if(chats.length > prevChats.length){
                const ids = prevChats.current.map((item)=>item.id);
                const ncc = chats.filter((item)=>!ids.includes(item.id))[0].id;
                const nc = chats[chats.length - 1].id;
                setNewChatID(ncc);
            }
        }
        prevChats.current = chats;
        
    },[chats]);

    console.log(chats)

    return (
        <div className={"navPromptWrapper"}  style={{}}>
            {chats&&Array.isArray(chats)&&chats.map((c, index) => (
                newChatID !== null && c.id === newChatID ? (
                    <NewNavChat chat={c} key={`chat_${index}`} />
                ) : (
                    <NavChat chat={c} key={`chat_${index}`} />
                )
            ))}
        </div>
    );
}
export default NavChatList;

