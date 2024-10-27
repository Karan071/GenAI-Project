import React from 'react';
import { RiSendPlane2Line } from 'react-icons/ri';

const Chatbox = () => {
    return (
        <div className="absolute inset-x-0 bottom-0 h-16 flex items-center px-10">
            <input
                type="text"
                placeholder="Type a message..."
                className="flex-grow p-2 border rounded-lg outline-none"
            />
            <button className="ml-2 p-2 text-green-500 hover:text-green-700">
                <RiSendPlane2Line size={24} />
            </button>
        </div>
    );
};

export default Chatbox;
