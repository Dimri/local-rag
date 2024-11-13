import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";

const PDFViewer = () => {
  const location = useLocation();
  const { fileUrl } = location.state || null;

  const [messages, setMessages] = useState([
    {
      sender: "Assistant",
      text: "hello!",
    },
  ]);
  const [currentMessage, setCurrentMessage] = useState("");

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    const newMessages = [...messages, { sender: "User", text: currentMessage }];
    setMessages(newMessages);
    setCurrentMessage("");

    try {
      const response = await axios.post("http://localhost:8000/chat", {
        message: currentMessage,
      });

      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "Assistant", text: response.data.reply },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          sender: "Assistant",
          text: "failed to get response from the server.",
        },
      ]);
    }
  };

  const handleInputChange = (event) => {
    setCurrentMessage(event.target.value);
  };

  return (
    <div className="flex min-h-screen bg-white">
      {/* Left Half: PDF Viewer */}
      <div className="w-1/2 border-r border-gray-400 p-4">
        <iframe src={fileUrl} className="w-full h-full" title="PDF Viewer" />
      </div>

      {/* Right Half: Chat UI */}
      <div className="w-1/2 p-4">
        <h2 className="text-2xl font-semibold mb-4">Chat</h2>
        <div className="border border-gray-300 p-2 h-3/4 overflow-auto">
          {/* Chat Messages */}
          {messages.map((msg, index) => (
            <div key={index} className="mb-2">
              <strong>{msg.sender}:</strong> {msg.text}
            </div>
          ))}
        </div>

        {/* Chat Input */}
        <div className="mt-4">
          <textarea
            value={currentMessage}
            onChange={handleInputChange}
            className="w-full p-2 border border-gray-300 rounded"
            rows="4"
            placeholder="Type your message..."
          ></textarea>
          <button
            onClick={handleSendMessage}
            className="mt-2 w-full bg-black text-white p-2 rounded"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;
