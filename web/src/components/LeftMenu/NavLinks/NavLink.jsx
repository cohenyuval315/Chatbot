
const NavLinks = ({ svg, link, text, setChatLog }) => {


  const handleClick = async (text) => {
    if (text === "Clear Conversations") setChatLog([]);
    if (text === "Log out") {
      try {


      } catch (error) {
        console.log("error happen during sign out", error);
      }
    }
  };

  return (
    <div onClick={handleClick}>
      
    </div>
  );
};

export default NavLinks;
