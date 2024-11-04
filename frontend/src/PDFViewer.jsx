import React from "react";
import { useLocation } from "react-router-dom";

const PDFViewer = () => {
  const location = useLocation();
  const { fileUrl } = location.state || null;
  // Cleanup the URL when the component unmounts
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
          <div className="mb-2">
            <strong>User:</strong> Hello, how can I help you?
          </div>
          <div className="mb-2">
            <strong>Assistant:</strong>
          </div>
          {/* Additional chat messages can be added here */}
        </div>

        {/* Chat Input */}
        <div className="mt-4">
          <textarea
            className="w-full p-2 border border-gray-300 rounded"
            rows="4"
            placeholder="Type your message..."
          ></textarea>
          <button className="mt-2 w-full bg-black text-white p-2 rounded">
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;
