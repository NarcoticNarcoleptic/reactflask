// components/Sidebar.js
import FileUploadComponent from './upload';
//import { useState } from 'react';
import CreateCollectionComponent from './createcollection';

export default function Sidebar() {
    return (
      <div className="w-1/3 bg-gray-200 p-4">
        <FileUploadComponent />
        <CreateCollectionComponent/>
      </div>
    );
  }