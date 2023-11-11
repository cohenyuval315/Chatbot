import React from "react";
import {useChat} from '../../context/ChatContext'
const NewChatButton = ({ setShowMenu }) => {
  const {onChatNew} = useChat();
  const createNewChat = () => {
    onChatNew()
    setShowMenu(false);
  }


  return (
    <div
      className="sideMenuButton"
      onClick={createNewChat}
    >
      <span>+</span>
      New chat
    </div>
  );
};

export default NewChatButton;
