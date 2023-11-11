import React, { useRef, useState } from "react";
import { useChat } from "../../context/ChatContext";

const ChatBoxInput = () => {
    const {inputDisable,onChatConverse} = useChat();
    const [inputPrompt, setInputPrompt] = useState("");
    const inputRef = useRef(null); 

    const handleChatSubmit = async (e) => {
        e.preventDefault();
        setInputPrompt("");
        if (inputRef.current) {
            inputRef.current.blur();
        }  
        if (inputPrompt.trim() !== "") {
            await onChatConverse(inputPrompt);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleChatSubmit(e);
        }
    };
    return (
        <form className="inputPromptWrapper" autoComplete="off" autoCorrect="off" >
            <input
            ref={inputRef} 
            name="inputPrompt"
            id=""
            className="inputPrompttTextarea"
            type={"text"}
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            disabled={inputDisable}
            style={inputDisable?{
                backgroundColor: "#2C2C36",
                color: "#666",
                cursor: "not-allowed",
                border: "1px solid #999"
            }:{}}
            autoFocus
            ></input>
            <button  style={{marginBottom:"5px",border: "none",background: "none"}} onKeyDown={handleKeyDown} onClick={handleChatSubmit}>

            <svg
                fill="#ADACBF"
                width={15}
                height={18}
                viewBox="0 0 32 32"
                xmlns="http://www.w3.org/2000/svg"
                stroke="#212023"
                strokeWidth={0}
            >
                <title>{"submit form"}</title>
                <path
                d="m30.669 1.665-.014-.019a.73.73 0 0 0-.16-.21h-.001c-.013-.011-.032-.005-.046-.015-.02-.016-.028-.041-.05-.055a.713.713 0 0 0-.374-.106l-.05.002h.002a.628.628 0 0 0-.095.024l.005-.001a.76.76 0 0 0-.264.067l.005-.002-27.999 16a.753.753 0 0 0 .053 1.331l.005.002 9.564 4.414v6.904a.75.75 0 0 0 1.164.625l-.003.002 6.259-4.106 9.015 4.161c.092.043.2.068.314.068H28a.75.75 0 0 0 .747-.695v-.002l2-27.999c.001-.014-.008-.025-.008-.039l.001-.032a.739.739 0 0 0-.073-.322l.002.004zm-4.174 3.202-14.716 16.82-8.143-3.758zM12.75 28.611v-4.823l4.315 1.992zm14.58.254-8.32-3.841c-.024-.015-.038-.042-.064-.054l-5.722-2.656 15.87-18.139z"
                stroke="none"
                />
            </svg>
            </button>
        </form>
    );
}
export default ChatBoxInput;