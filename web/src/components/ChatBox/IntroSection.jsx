import React from "react";
import { useChat } from "../../contexts/ChatContext";

const IntroSection = () => {
  
  return (
    <div id="introsection" style={{paddingLeft:"150px",paddingRight:"100px"}}>
      
      <p style={{color:"white",fontSize:"40px"}}>Welcome!</p>
      <p>Hello and welcome to Yuval Cohen's chatbot! 🤖</p>
      <p>A serverless chatbot that allows you engage with various machine learning models, with some basic features which includes auto save conversations, and ability to delete conversations.</p>
      <u>
        <li>
          <strong>GitHub Link:</strong> <a style={{ color: 'gray' }}href="https://github.com/cohenyuval315/Chatbot">ChatBot GitHub Repository</a>
        </li>
        <li>
        <strong>LinkedIn:</strong> <a style={{ color: 'gray' }}href="https://www.linkedin.com/in/yc315/">Linkdin Profile</a>
        </li>
        <li>
          technology stack:
          <ul>
            <li>
            <strong>frontend:</strong>  React
            </li>
            <li><strong>backend:</strong>
              <ul>
                <li>Localstack</li>
                <li>AWS SAM(Serverless Application Model)</li>
                <li>AWS ApiGateWay</li>
                <li>AWS Lambda</li>
                <li>AWS DynamoDB</li>
              </ul>
            </li>
          </ul>
        </li>
      </u>
      
      
      <p style={{fontSize:"20px"}}>Models Information:</p>
      <ModelCardsTabs/>
      <p>Feel free to explore the capabilities of the chatbot, ask questions, or engage in a conversation. Thank you for using my chatbot. If you have any feedback or suggestions, feel free to let me know. Happy chatting! 😊</p>
    
    </div>
  );
};


const ModelCardsTabs = () => {
  const { modelOptions } = useChat();

  return (
    <div className="model-cards-container">
      <ul className="model-cards-list">
        {modelOptions && modelOptions.map((option, index) => (
          <li key={index} className="model-card-item">
            <ModelCard model_data={option} />
          </li>
        ))}
      </ul>
    </div>
  );
};

const ModelCard = ({ model_data }) => {
  return (
    <div className="model-card">
      <p>
        <strong>Model Used:</strong> {model_data.model_name}
      </p>
      <p>
        <strong>Hugging Face Link:</strong>{' '}
        <a target="_blank" style={{ color: 'gray' , cursor:"pointer"}} href={model_data.model_link} >
          Huggingface Model Link
        </a>
      </p>
    </div>
  );
};


export default IntroSection;
