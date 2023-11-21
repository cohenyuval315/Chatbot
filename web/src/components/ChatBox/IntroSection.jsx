import React from "react";

const IntroSection = () => {
  return (
    <div id="introsection" style={{paddingLeft:"150px"}}>
      <p>
        <h1 style={{color:"white",fontSize:"40px"}}>Welcome!</h1>
        <p>
        Hello and welcome to Yuval Cohen's chatbot! 🤖

        </p>
        <p>
            A serverless chatbot that allows you to save conversations, delete them, and continue engaging with the bot using a machine learning model.
        </p>
        <h2>About the ChatBot:</h2>

        <p>
        <strong>frontend:</strong> React
        </p>        
        <p>
        <strong>backend:</strong> 
        <ul>
          <li>Localstack</li>
          <li>AWS SAM(Serverless Application Model)</li>
          <li>AWS ApiGateWay</li>
          <li>AWS Lambda</li>
          <li>AWS DynamoDB</li>
          </ul>
        </p>

        <h2>Model Information</h2>
        <ul>
          <li>
            <strong>Model Used:</strong> google/flan-t5-small
          </li>
          <li>
            <strong>Hugging Face Link:</strong> <a style={{ color: 'gray' }}href="https://huggingface.co/google/flan-t5-small">Huggingface Model Link</a> 
          </li>
          <li>
            <strong>GitHub Link:</strong> <a style={{ color: 'gray' }}href="https://github.com/cohenyuval315/Chatbot">ChatBot GitHub Repository</a>
          </li>
          <li>
            <strong>LinkedIn:</strong> <a style={{ color: 'gray' }}href="https://www.linkedin.com/in/yc315/">Linkdin Profile</a>
          </li>
        </ul>

        <p>
          Feel free to explore the capabilities of the chatbot, ask questions, or engage in a conversation.
        </p>

        <h2>Enjoy your ChatBot experience!</h2>
        <p>
          Thank you for using my chatbot. If you have any feedback or suggestions, feel free to let me know. Happy chatting! 😊
        </p>
      </p>
    </div>
  );
};

export default IntroSection;
