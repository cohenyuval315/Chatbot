import React from "react";
import SvgComponent from "../General/SvgComponent";
import Avatar from "../General/Avatar";
import BotResponse from "./BotResponse";
import Error from "../General/Error";
import Loading from "../General/Loading";
import { useChat } from "../../context/ChatContext";

const BotMessage = ({chatLogRef,response,animate}) => {
    const {error} = useChat();
    return (

        <div className="botMessageMainContainer">
            <div style={{lineBreak:"anywhere"}} className="botMessageWrapper">
            <Avatar bg="#11a27f" className="openaiSVG">
                <SvgComponent w={41} h={41}  />
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