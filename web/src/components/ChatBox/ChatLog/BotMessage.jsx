import React from "react";
import SvgComponent from "../../General/BotAvatar";
import Avatar from "../../General/Avatar";
import BotResponse from "./BotResponse";
import Error from "../../General/ErrorMessage";
import Loading from "./ChatLoading";
import { useChat } from "../../../contexts/ChatContext";

const BotMessage = ({chatLogRef,response,animate}) => {
    const {error} = useChat();
    return (

        <div className="botMessageMainContainer">
            <div style={{lineBreak:"anywhere"}} className="botMessageWrapper">
            <Avatar bg="black" className="botSVG" text={"bot"}>
                <SvgComponent w={18} h={20}  />
                
            </Avatar>
            {response ? (
                <BotResponse
                    response={response}
                    chatLogRef={chatLogRef}
                    animate={animate}
                />
            ) : error ? (
                <Error err={error} />
            ) : (
                <Loading />
            )}
            </div>
        </div>
    );
}
export default BotMessage;