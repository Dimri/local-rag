import React, { useState, useRef } from "react";
import axios from "axios";
import { FaUpload } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [fileUrl, setFileUrl] = useState(null);
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setFileUrl(URL.createObjectURL(file));
    console.log("Selected file:", file);
  };

  const handleUpload = async (event) => {
    event.stopPropagation();
    if (selectedFile) {
      const formData = new FormData();
      formData.append("file", selectedFile);
      try {
        const response = await axios.post(
          "http://localhost:8000/upload/",
          formData,
          {
            headers: { "Content-Type": "multipart/form-data" },
          }
        );
        console.log("File uploaded successfully:", response.data);
        setSelectedFile(null);
        navigate("/view-pdf", { state: { fileUrl: fileUrl } });
      } catch (error) {
        console.error("Error uploading file:", error);
        alert("Failed to upload file. Please try again.");
      }
    } else {
      alert("Please select a file first.");
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      console.log("Dropped file: ", file);
    } else {
      console.log("Dropped nothing!");
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white text-black">
      <h1 className="text-6xl antialiased font-bold mb-20">
        Chat with your PDF!
      </h1>
      <div
        className={`border-dashed border-2 border-gray-400 p-20 mx-auto justify-center flex flex-col items-center cursor-pointer ${
          isDragging ? "border-black bg-gray-200" : "border-gray-400"
        }
      `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        <FaUpload className="mx-auto w-20 h-20 opacity-10" />
        <div className="border-dashed p-10">
          <h2 className="text-center text-2xl antialiased font-semibold">
            Choose file or drag and drop
          </h2>
        </div>
        <button
          className="text-lg font-bold py-2 bg-black border-2 border-black text-white text-center rounded-xl w-32 mx-auto hover:border-2 hover:border-black hover:text-black hover:bg-white"
          onClick={handleUpload}
        >
          Upload
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        ></input>
      </div>
      {selectedFile && (
        <p className="mt-4 text-gray-700">Selected file: {selectedFile.name}</p>
      )}
    </div>
  );
};

export default FileUpload;
