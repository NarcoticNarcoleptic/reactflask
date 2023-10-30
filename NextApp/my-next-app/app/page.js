"use client"

import Image from 'next/image';
import ApiRequest from './components/chat';
//import FileUploadComponent from './components/upload';
import Sidebar from './components/sidebar';
import Navbar from './components/navbar'

export default function Home() {
  return (
    
    <main className="flex min-h-screen">
      <Navbar/>
      <Sidebar />
      <div className="flex-grow flex justify-center items-center">
        <ApiRequest />
      </div>
    </main>
  );
}




