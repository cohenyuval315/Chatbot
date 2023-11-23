import React, { useState } from 'react';

const Dropdown = ({ initialOption , options, onSelect ,labelProperty,valueProperty }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState(initialOption);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleSelectOption = (option) => {
    setSelectedOption(option);
    onSelect(option);
    toggleDropdown();
  };

  return (
    <div className="dropdown">
      <div className="dropdown-toggle" onClick={toggleDropdown}>
        {selectedOption ? selectedOption[labelProperty] : 'Select an option'}
      </div>
      {isOpen && (
        <ul className="dropdown-options">
          {options&&Array.isArray(options)&&options.map((option) => (
            
            <li key={option[valueProperty]} onClick={() => handleSelectOption(option)}>
              {option[labelProperty]}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Dropdown;
