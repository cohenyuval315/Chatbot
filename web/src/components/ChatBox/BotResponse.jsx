import React, {  useEffect } from "react";
import { useState } from "react";
import CursorSVG from "../General/CursorSVG";
import { useChat } from "../../context/ChatContext";

const BotResponse = ({chatLogRef,response,animate}) => {
  const [isPrinting, setIsPrinting] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');
  const {printInterval} = useChat();

  // useEffect(()=>{
  //   console.debug("msg interval");
  //   console.debug("msg:", msg);
  //   console.debug("botResponse:", botResponse);
  //   let index = 1;
  //   let message = setInterval(() => {
  //       if (!isPrinting) {
  //           clearInterval(message);
  //           return;
  //       }
  //       setMsg(botResponse.slice(0, index));
  //       if (index >= botResponse.length) {
  //           clearInterval(message);
  //           setIsButtonStopVisible(false);
  //       }
  //       index++;
    
  //       // scroll bottom
  //       if (chatLogRef !== undefined) {
  //           chatLogRef.current.scrollIntoView({
  //           behavior: "smooth",
  //           block: "end",
  //           });
  //       }

  //       }, printInterval);
  //   return () => {
  //     clearInterval(message);
  //     onChatFinish();
  //   };
    
  // },[chatLogRef,botResponse,msg])



  useEffect(() => {
    if (chatLogRef !== undefined && chatLogRef !== null) {
      chatLogRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'end',
      });
    }        
    if(!response){
      return;
    }
    //setIsPrinting(false);
  
    let i = 0;
    
    const intervalId = setInterval(() => {
      setCurrentMessage(response.slice(0, i));
      if(isPrinting === false){

      }
      i++;
      if (i > response.length) {
        clearInterval(intervalId);
        setIsPrinting(false);
      }
    }, printInterval);
  
    return () => {
      clearInterval(intervalId);
      setIsPrinting(true);
    };    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatLogRef,response]);

  const feedback = () => {

  }

  return (
    <div> 
      <pre id="" style={{ whiteSpace: 'pre-wrap' }}>
        {animate?(<>
          {currentMessage}
          {isPrinting && <CursorSVG />}
          {!isPrinting && (
          <div>
            {/* <button>good</button>
            <button>bad</button> */}
          </div>)}
        </>) : response}
      </pre>
    </div>
  );
};

export default BotResponse;
