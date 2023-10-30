import React, { useState } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const PDF_FILE_PATH = "pdf_folder/langchain-cohere-qdrant-retrieval.pdf";

const insertDocument = async (file) => {
  const formData = new FormData();
  formData.append('pdf', file); // Use 'pdf' as the key to match the Flask route

  const response = await fetch('http://localhost:5000/upload', {
    mode: 'cors',
    method: 'POST',
    body: formData,
  });

  const responseText = await response.text();
  return responseText;
};

const FileUploadComponent = () => {
  const [isRequestSent, setRequestSent] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const sendRequest = async () => {
    if (selectedFile) {
      try {
        setRequestSent(true);

        const responseText = await insertDocument(selectedFile);

        if (responseText === "PDF uploaded successfully!") {
          console.log("PDF file uploaded successfully.");
        } else if (responseText === "Rate limit reached. Please try again later.") {
          console.log("Rate limit reached. Please try again later.");
        } else {
          console.error("File upload failed.");
        }
      } catch (error) {
        console.error("Failed to upload the PDF file:", error);
      } finally {
        setRequestSent(false);
      }
    } else {
      console.error("No file selected.");
    }
  };

  return (
    <div className="p-4">
      <div className="mb-4 mt-10 ">
      
        <input
          accept=".pdf"
          id="file-input"
          type="file"
          className="hidden"
          onChange={handleFileChange}
        />
        <label htmlFor="file-input" className="cursor-pointer p-1 bg-blue-500 text-white rounded-md hover:bg-blue-600">
          <CloudUploadIcon className="w-6 h-6" />
          select pdf
        </label>
      </div>

      <div className="mt-1">
        <Button
          className={`p-1 bg-blue-500 text-white rounded-md hover:bg-blue-600 ${isRequestSent || !selectedFile ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={sendRequest}
        >
          <CloudUploadIcon className="w-6 h-6" />
          upload
        </Button>
      </div>
    </div>
  );
};

export default FileUploadComponent;
