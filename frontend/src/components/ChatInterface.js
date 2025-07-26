import React, { useState, useEffect, useRef, useCallback } from 'react';
import Message from './Message';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your PartSelect assistant. I can help you find refrigerator and dishwasher parts, check compatibility, provide installation guides, and troubleshoot issues. How can I help you today?",
      sender: 'assistant',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId] = useState(() => `conv_${Date.now()}`);
  
  // Refs for accessibility and UX
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const messagesContainerRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const focusInput = useCallback(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Focus input on mount for better UX
  useEffect(() => {
    focusInput();
  }, [focusInput]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post('/chat', {
        message: messageToSend,
        conversation_id: conversationId
      }, {
        timeout: 45000  // Increased to 45 seconds for enhanced features
      });

      const assistantMessage = {
        id: Date.now() + 1,
        text: response.data.message,
        sender: 'assistant',
        timestamp: response.data.timestamp,
        outOfScope: response.data.out_of_scope,
        error: response.data.error
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      let errorText = 'Sorry, I encountered an error. Please try again.';
      
      if (error.code === 'ECONNABORTED') {
        errorText = 'Request timed out. Please try again.';
      } else if (error.response?.status === 500) {
        errorText = 'Server error. Please try again later.';
      }

      const errorMessage = {
        id: Date.now() + 1,
        text: errorText,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // Refocus input after sending message
      setTimeout(() => focusInput(), 100);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestedQuestions = [
    "How can I install part PS11752778?",
    "Is part WPW10082853 compatible with WDT780SAEM1?",
    "My ice maker isn't working",
    "Find water filters for Whirlpool fridge"
  ];

  const handleSuggestedQuestion = (question) => {
    setInputValue(question);
    focusInput();
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  return (
    <div 
      className="chat-interface" 
      role="application" 
      aria-label="PartSelect Assistant Chat"
    >
      {/* Live region for screen reader announcements */}
      <div 
        aria-live="polite" 
        aria-atomic="true" 
        className="sr-only"
        role="status"
        aria-label="Chat status"
      >
        {isLoading && "PartSelect Assistant is typing..."}
        {messages.length > 1 && `${messages.length - 1} messages in conversation`}
      </div>

      <div 
        className="messages-container"
        ref={messagesContainerRef}
        role="log"
        aria-live="polite"
        aria-label="Chat messages"
        tabIndex="0"
      >
        {messages.map((message, index) => (
          <Message 
            key={message.id} 
            message={message}
            isLatest={index === messages.length - 1}
          />
        ))}
        
        {isLoading && (
          <div 
            className="loading-indicator"
            role="status"
            aria-label="PartSelect Assistant is typing"
          >
            <div className="typing-dots" aria-hidden="true">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className="sr-only">Assistant is typing a response...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div 
          className="suggested-questions"
          role="region"
          aria-label="Suggested questions"
        >
          <p id="suggestions-heading">Try asking:</p>
          <div 
            className="suggestions"
            role="group"
            aria-labelledby="suggestions-heading"
          >
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                className="suggestion-btn"
                onClick={() => handleSuggestedQuestion(question)}
                type="button"
                aria-describedby="suggestions-heading"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      <div 
        className="input-container"
        role="region"
        aria-label="Message input"
      >
        <label htmlFor="message-input" className="sr-only">
          Type your message about refrigerator or dishwasher parts
        </label>
        <textarea
          id="message-input"
          ref={inputRef}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask about refrigerator or dishwasher parts..."
          className="message-input"
          rows="1"
          disabled={isLoading}
          aria-describedby="input-help"
          maxLength={1000}
        />
        <div id="input-help" className="sr-only">
          Press Enter to send your message, or Shift+Enter for a new line. Maximum 1000 characters.
        </div>
        
        <button 
          onClick={sendMessage} 
          className="send-button"
          disabled={!inputValue.trim() || isLoading}
          type="button"
          aria-label={isLoading ? "Sending message..." : "Send message"}
          aria-describedby="send-help"
        >
          <span aria-hidden="true">
            {isLoading ? '⏳' : '→'}
          </span>
          <span className="send-button-text">
            {isLoading ? 'Sending...' : 'Send'}
          </span>
        </button>
        <div id="send-help" className="sr-only">
          Send your message to the PartSelect Assistant
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;