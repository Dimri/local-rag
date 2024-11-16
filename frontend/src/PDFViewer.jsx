import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { useLocation, useNavigate } from "react-router-dom";

import axios from "axios";

const PDFViewer = () => {
  const location = useLocation();
  const { fileUrl } = location.state || null;
  const navigate = useNavigate();

  const [messages, setMessages] = useState([
    {
      sender: "Assistant",
      text: "Start asking questions!",
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
      console.log("response from LLM", response);
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

  const goToHomepage = () => {
    navigate("/");
  };

  return (
    <div className="flex min-h-screen bg-white">
      {/* Left Half: PDF Viewer */}
      <div className="w-1/2 border-r border-gray-400 p-4 overflow-auto h-screen">
        <iframe src={fileUrl} className="w-full h-full" title="PDF Viewer" />
      </div>

      {/* Right Half: Chat UI */}
      <div className="w-1/2 p-4 overflow-auto h-screen">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold mb-4">Chat</h2>
          <button
            onClick={goToHomepage}
            className="mb-4 px-4 py-2 font-bold  bg-black text-white rounded hover:bg-gray-600"
          >
            Home
          </button>
        </div>
        <div className="border border-gray-300 p-2 h-3/4 overflow-auto">
          {/* Chat Messages */}
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`mb-4 flex ${
                msg.sender === "User" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-md w-auto p-3 rounded-lg ${
                  msg.sender === "User"
                    ? "bg-blue-100 text-right"
                    : "bg-gray-100 text-left"
                }`}
              >
                <ReactMarkdown className="prose prose-sm prose-blue">
                  {msg.text}
                </ReactMarkdown>
              </div>
            </div>
          ))}
        </div>

        {/* Chat Input */}
        <div className="flex items-center px-3 py-2 rounded mt-2">
          <textarea
            value={currentMessage}
            onChange={handleInputChange}
            className="min-h-12 rounded resize-y block mx-2 p-2.5 w-full text-sm text-gray-900 bg-white border border-gray-300 scrollbar-none"
            rows="1"
            placeholder="Your message..."
          ></textarea>
          <button
            type="submit"
            onClick={handleSendMessage}
            className="h-12 inline-flex justify-center items-center p-3 bg-black rounded cursor-pointer dark:hover:bg-gray-600"
          >
            <svg
              className="w-5 h-5 rotate-90 rtl:-rotate-90"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="white"
              viewBox="0 0 18 20"
            >
              <path d="m17.914 18.594-8-18a1 1 0 0 0-1.828 0l-8 18a1 1 0 0 0 1.157 1.376L8 18.281V9a1 1 0 0 1 2 0v9.281l6.758 1.689a1 1 0 0 0 1.156-1.376Z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;
