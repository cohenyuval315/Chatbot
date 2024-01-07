import React, { useState } from "react";
import Dropdown from "../../General/Dropdown";
import { useChat } from "../../../contexts/ChatContext";
import ChatHeaderDeleteModal from "./ChatHeaderDeleteModal";

const ChatHeader = ({title,onDelete}) => {
  const {
    selectedModelOption,
    modelOptions,
    onModelSelect,
    dropdownLabelProperty,
    dropdownValueProperty
  } = useChat()

  const [showModal, setShowModal] = useState(false);
  const handleDeleteClick = (e) => {
    e.preventDefault();
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  }
    return (
      <>
        <div style={headerStyle}>
          <div>
            <div>
              Model:
            </div>
            <div>
              <Dropdown   
                  initialOption={selectedModelOption} 
                  options={modelOptions} 
                  onSelect={onModelSelect} 
                  labelProperty={dropdownLabelProperty} 
                  valueProperty={dropdownValueProperty}
              />
            </div>
          </div>
          <div style={titleContainerStyle}>
            <div style={titleStyle}>{title}</div>
          </div>
          <div style={buttonContainerStyle}>
            {onDelete&&(<button style={buttonStyle} onClick={handleDeleteClick}>Delete</button>)}
          </div>
        </div>
        {showModal && (
            <ChatHeaderDeleteModal close={closeModal}/>
        )}
      </>
    );
}



const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px',
    
    
    // backgroundColor: '#eee',
  };
  
  const titleContainerStyle = {
    flex: '1', // This makes the title container take up the available space
    textAlign: 'center', // Center the title horizontally
  };
  
  const titleStyle = {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    paddingBottom:'5px'
  };
  
  const buttonContainerStyle = {
    display: 'flex',
    marginRight:'10px',
  };
  
  const buttonStyle = {
    marginLeft: '10px',
    padding: '10px 15px',
    backgroundColor: '#202022', 
    color: '#d1d5db', 
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  };
  

export default ChatHeader;