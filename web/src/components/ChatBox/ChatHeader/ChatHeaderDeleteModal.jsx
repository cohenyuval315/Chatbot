import { useChat } from "../../../contexts/ChatContext";

const ChatHeaderDeleteModal = ({close}) => {
    const {deleteChat} = useChat();
    const handleOverlayClick = () => {
      close()
    };
    
    const handleConfirmDelete = async () => {
      close()
      await deleteChat();
      
    };
    const handleCancelDelete = () => {
      close()
      
    };
    return (
      <div>
        <div style={overlayStyle}  onClick={handleOverlayClick}></div>
        <div style={modalStyle}>
          <p>Are you sure you want to delete?</p>
          <div style={modalButtonContainerStyle}>
            <button style={confirmButtonStyle}  onClick={handleConfirmDelete}>Yes</button>
            <button style={cancelButtonStyle}  onClick={handleCancelDelete}>No</button>
          </div>
        </div>
      </div>
    )
  }
  

  const modalStyle = {
    position: "fixed",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    padding: "20px",
    width: "400px",
    backgroundColor: "#282c34",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    zIndex: 1000,
    textAlign: "center", 
  };
  
  const overlayStyle = {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    zIndex: 999,
  };
  
  
  const modalButtonContainerStyle = {
    marginTop: "30px", // Add some space between buttons and modal content
    alignItems:"center",
    justifyContent:"space-between"
  };
  
  const confirmButtonStyle = {
    marginRight: '10px',
    // padding: '10px 15px',
    backgroundColor: '#e74c3c',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    height:"30px",
    width:"150px"
  };
  
  const cancelButtonStyle = {
    // padding: '10px 15px',
    height:"30px",
    backgroundColor: '#353540',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    width:"150px"
  };
  

export default ChatHeaderDeleteModal