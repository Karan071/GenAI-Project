import React, { useState } from 'react';
import imgIcon from "../assets/icon.png";
import { LuUploadCloud } from "react-icons/lu";
import axios from 'axios';

const Navbar = () => {
  const [files, setFiles] = useState([]);

  const handleFileChange = (event) => {
    setFiles(Array.from(event.target.files));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    const formData = new FormData();
    files.forEach(file => {
      formData.append('docs', file);
    });

    try {
      const response = await axios.post('http://localhost:8000/ingest', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log(response.data);
      setFiles([]); // Clear files after successful upload
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  };

  return (
    <div className="flex flex-col items-center p-4 shadow-md bg-white">
      {/* Navbar */}
      <div className="flex justify-between items-center w-full">
        <img className="h-11" src={imgIcon} alt="Icon" />
        
        {/* Upload Button */}
        <label className="flex items-center text-white bg-green-700 hover:bg-green-800 focus:outline-none focus:ring-4 focus:ring-green-300 font-medium rounded-full text-sm px-5 py-2.5 cursor-pointer">
          <LuUploadCloud className="mr-2" size={20} />
          Upload
          <input 
            type="file" 
            name="Upload" 
            id="upload" 
            className="hidden" 
            multiple 
            onChange={handleFileChange}
          />
        </label>
        
        <button 
          onClick={handleUpload} 
          disabled={files.length === 0}
          className={`ml-2 p-2 text-white bg-green-500 rounded-lg ${files.length === 0 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-green-600'}`}
        >
          Submit
        </button>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-4 w-full bg-gray-100 p-2 rounded-lg shadow-inner">
          <p className="text-sm font-semibold mb-2">Selected Files:</p>
          <ul className="text-sm text-gray-700 space-y-1">
            {files.map((file, index) => (
              <li key={index} className="flex items-center justify-between">
                <span>{file.name}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Navbar;