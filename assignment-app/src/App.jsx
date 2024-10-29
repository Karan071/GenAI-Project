import React, { useState } from 'react';
import Chatbox from './Components/Chatbox';
import Conversations from './Components/Conversations';
import Navbar from './Components/Navbar';
import './index.css';

function App() {
  const [messages, setMessages] = useState([]);

  const addMessage = (userMessage, aiResponse) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { type: 'user', text: userMessage },
      { type: 'ai', text: aiResponse }
    ]);
  };

  return (
    <>
      <Navbar />
      <Conversations messages={messages} />
      <Chatbox onNewMessage={addMessage} />
    </>
  );
}

export default App;