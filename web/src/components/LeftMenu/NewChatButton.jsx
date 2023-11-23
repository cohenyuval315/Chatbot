import React from "react";
import {useChat} from '../../contexts/ChatContext'

const NewChatButton = () => {
  const {onNewChatSelect} = useChat();

  const onNewPress = async () => {
    await onNewChatSelect();
  }

  return (
    <div
      className="sideMenuButton"
      onClick={onNewPress}
    >
      <span>+</span>
      New chat
    </div>
  );
};

export default NewChatButton;
