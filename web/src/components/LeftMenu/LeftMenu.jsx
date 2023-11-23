import React from "react";
import NewChatButton from "./NewChatButton";
import NavChatList from './NavChatsList'
import { useChat } from "../../contexts/ChatContext";
import LeftMenuLoading from "./LeftMenuLoading";

const LeftMenu = () => {
    const {loading} = useChat();
    return (
        <>
            {loading ? (<>
                <LeftMenuLoading/>
            </>) : (
                <aside className="sideMenu">
                    <NewChatButton />
                    <NavChatList/>
                </aside>
            )}
        </>

    );
}
export default LeftMenu;
