import React from "react";

const Avatar = ({ children, bg, className,text }) => {
  return (
    <div style={{flexDirection:"column"}}>
      <div id="avatar" style={{ backgroundColor: `${bg}`}}>
        <div className={className}>{children}</div>
      </div>
      <div style={{
          fontSize:14,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
      }}
      >{text}</div>  
    </div>
  );
};

export default Avatar;
