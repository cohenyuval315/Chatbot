import React from "react";

const NewChat = () => {
  return (
    <div id="newChat" style={styles.container}>
      <p style={styles.heading}>New Chat</p>
    </div>
  );
};


const styles = {
  container: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    
  },
  heading: {
    color: 'rgba(128, 128, 128, 0.1)',
    fontSize: '70px',
    paddingTop:"300px",
    fontWeight: 'bold', 
    textShadow: '2px 2px 4px rgba(0, 0, 0, 0)',
    
  },
};
export default NewChat;
