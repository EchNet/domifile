import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from "react-router-dom"

import { FullScreenProvider } from './context/FullScreenContext'
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <FullScreenProvider>
      <App/>
    </FullScreenProvider>
  </BrowserRouter>
);
