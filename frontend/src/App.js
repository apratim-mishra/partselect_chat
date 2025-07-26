

import React from 'react';
import ChatInterface from './components/ChatInterface';
import './index.css';
import './styles/App.css';

function App() {
  return (
    <div className="App">
      {/* Skip to main content for accessibility */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      
      <header className="App-header" role="banner">
        <div className="header-content">
          <h1>
            <span aria-hidden="true">🔧</span>
            PartSelect Assistant
          </h1>
          <p>Get expert help with refrigerator and dishwasher parts</p>
        </div>
      </header>
      
      <main 
        id="main-content" 
        className="App-main" 
        role="main"
        aria-label="Chat interface"
      >
        <ChatInterface />
      </main>
      
      {/* Footer for additional info if needed */}
      <footer className="App-footer" role="contentinfo" aria-hidden="true">
        <div className="footer-content">
          <p className="sr-only">
            PartSelect AI Assistant - Helping you find and install appliance parts
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

