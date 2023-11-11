import React from "react";
import NavChat from "./NavChat";
import NewChatButton from "./NewChatButton";
import {useChat} from '../../context/ChatContext'

const SideMenu = (props) => {
    const {chats} = useChat();
    return (
        <aside className="sideMenu">
            <NewChatButton setShowMenu={props.setShowMenu} />
            <div className="navPromptWrapper">
                {chats.map((chat, index) =><NavChat title={chat.title} key={`chat_${index}`} />)}
            </div>
            {/* <NavLinksContainer chatLog={chatLog} setChatLog={setChatLog} /> */}
        </aside>
    );
}
export default SideMenu;
