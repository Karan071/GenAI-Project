import React from 'react';
import imgIcon from "../assets/icon.png";
import { LuUploadCloud } from "react-icons/lu";

const Navbar = () => {
  return (
    <div className="flex justify-between items-center p-4 shadow-md bg-white">
        {/* Logo */}
        <img className="h-11" src={imgIcon} alt="Icon" />
        
        {/* Upload Button */}
        <button
          type="button"
          className="flex items-center text-white bg-green-700 hover:bg-green-800 focus:outline-none focus:ring-4 focus:ring-green-300 font-medium rounded-full text-sm px-5 py-2.5 text-center dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800"
        >
          <LuUploadCloud className="mr-2" size={20} />
          Upload
        </button>
    </div>
  );
};

export default Navbar;
