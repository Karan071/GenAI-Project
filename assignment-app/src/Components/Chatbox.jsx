import React, { useState } from 'react';
import { RiSendPlane2Line } from 'react-icons/ri';
import axios from 'axios';

const Chatbox = ({ onNewMessage }) => {
  const [message, setMessage] = useState('');

  const handleSend = async () => {
    if (!message) return;

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        query: message
      });
      onNewMessage(message, response.data.response);
      setMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="fixed inset-x-0 bottom-0 bg-white shadow-md h-16 flex items-center px-4">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message..."
        className="flex-grow p-2 border rounded-lg outline-none"
      />
      <button onClick={handleSend} className="ml-2 p-2 text-green-500 hover:text-green-700">
        <RiSendPlane2Line size={24} />
      </button>
    </div>
  );
};

export default Chatbox;