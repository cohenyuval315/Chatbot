import React, { useEffect, useRef, useState } from "react";
import SideMenu from "../components/SideMenu/SideMenu";
import ChatBox from "../components/ChatBox/ChatBox";
import { useChat } from "../context/ChatContext";
import AppLoading from "./AppLoading";

const Chat = () => {
  const [showMenu, setShowMenu] = useState(true);
  const {loading} = useChat();
  const props = {
    showMenu:showMenu,
    setShowMenu:setShowMenu,
  }
  
  return (
    <>
      {!loading ? (<>
        {/* <DrawerMenu props={props} chatLog={chatLog} setChatLog={setChatLog} setShowMenu={setShowMenu} showMenu={showMenu}/> */}
        <SideMenu {...props} />
        <ChatBox {...props} />
      </>) : <AppLoading/>}

    </>
  );
};

export default Chat;