import React from 'react';
import ai from "../assets/ai.png";
import profile from "../assets/profile.png";

const Conversations = ({ messages }) => {
  return (
    <div className="m-10 p-4 bg-gray-100 rounded-lg shadow-md max-h-[70vh] overflow-y-auto">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex items-start space-x-3 mb-4 ${message.type === 'user' ? 'flex-row' : 'flex-row-reverse'}`}
        >
          <img
            className="w-10 h-10 rounded-full"
            src={message.type === 'user' ? profile : ai}
            alt={message.type === 'user' ? "User" : "AI"}
          />
          <div
            className={`max-w-xs p-3 rounded-lg ${
              message.type === 'user' ? 'bg-green-500 text-white' : 'bg-gray-200'
            }`}
          >
            {message.text}
          </div>
        </div>
      ))}
    </div>
  );
};

export default Conversations;