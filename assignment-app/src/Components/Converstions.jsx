import React from 'react';
import ai from "../assets/ai.png";
import profile from "../assets/profile.png";
// import Ai from "./favicon.png"

const Conversations = () => {
  return (
    <div className="m-10 p-10 bg-gray-100 rounded-lg shadow-md">
      
      {/* User Message */}
      <div className="flex items-center justify-start space-x-3 mb-4">
        <img className="w-10 h-10 rounded-full" src={profile} alt="User" />
        <div className="max-w-xs p-3 bg-green-500 text-white rounded-lg">
          I need some help with my account.
        </div>
      </div>

      {/* AI/Server Reply */}
      <div className="flex items-center justify-end space-x-3 mb-4">
        <div className="max-w-xs p-3 bg-gray-200 rounded-lg">
          Hello! How can I help you today?
        </div>
        <img className="w-10 h-10 rounded-full" src={ai} alt="AI" />
      </div>

      {/* Additional messages can be added here in the same format */}
      
    </div>
  );
};

export default Conversations;
