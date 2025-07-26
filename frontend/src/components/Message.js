import React, { memo } from 'react';
import ProductCard from './ProductCard';

const Message = memo(({ message, isLatest = false }) => {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Enhanced text formatter to handle structured content
  const formatText = (text) => {
    if (!text) return null;

    // Split text into lines for processing
    const lines = text.split('\n');
    const elements = [];
    let currentList = [];
    let inList = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      if (!line) {
        // Handle empty lines
        if (inList && currentList.length > 0) {
          elements.push(
            <ul key={`list-${i}`} className="instruction-list" role="list">
              {currentList.map((item, idx) => (
                <li key={idx} role="listitem" dangerouslySetInnerHTML={{ __html: formatInlineText(item) }} />
              ))}
            </ul>
          );
          currentList = [];
          inList = false;
        }
        elements.push(<div key={`break-${i}`} className="line-break" />);
        continue;
      }

      // Handle headers (### text)
      if (line.startsWith('### ')) {
        if (inList && currentList.length > 0) {
          elements.push(
            <ul key={`list-before-${i}`} className="instruction-list" role="list">
              {currentList.map((item, idx) => (
                <li key={idx} role="listitem" dangerouslySetInnerHTML={{ __html: formatInlineText(item) }} />
              ))}
            </ul>
          );
          currentList = [];
          inList = false;
        }
        const headingText = formatInlineText(line.substring(4));
        elements.push(
          <h3 key={`header-${i}`} className="section-header">
            {headingText}
          </h3>
        );
        continue;
      }

      // Handle bullet points (* text or - text)
      const bulletMatch = line.match(/^[\*\-]\s+(.+)/);
      if (bulletMatch) {
        inList = true;
        currentList.push(bulletMatch[1]);
        continue;
      }

      // Handle numbered lists (1. text, 2. text, etc.)
      const listMatch = line.match(/^\d+\.\s+(.+)/);
      if (listMatch) {
        inList = true;
        currentList.push(listMatch[1]);
        continue;
      }

      // Handle regular lines
      if (inList && currentList.length > 0) {
        elements.push(
          <ul key={`list-${i}`} className="instruction-list" role="list">
            {currentList.map((item, idx) => (
              <li key={idx} role="listitem" dangerouslySetInnerHTML={{ __html: formatInlineText(item) }} />
            ))}
          </ul>
        );
        currentList = [];
        inList = false;
      }

      // Handle key-value pairs (Key: Value)
      if (line.includes(':') && !line.includes('?') && line.split(':').length === 2) {
        const [key, value] = line.split(':');
        if (key.trim().length < 30) { // Likely a label
          elements.push(
            <div key={`kv-${i}`} className="info-row" role="group">
              <span className="info-label">{formatInlineText(key.trim())}:</span>
              <span className="info-value">{formatInlineText(value.trim())}</span>
            </div>
          );
          continue;
        }
      }

      // Regular paragraph
      elements.push(
        <p key={`para-${i}`} className="message-paragraph">
          <span dangerouslySetInnerHTML={{ __html: formatInlineText(line) }} />
        </p>
      );
    }

    // Handle any remaining list items
    if (inList && currentList.length > 0) {
      elements.push(
        <ul key="final-list" className="instruction-list" role="list">
          {currentList.map((item, idx) => (
            <li key={idx} role="listitem" dangerouslySetInnerHTML={{ __html: formatInlineText(item) }} />
          ))}
        </ul>
      );
    }

    return elements;
  };

  // Format inline text (bold, part numbers, etc.)
  const formatInlineText = (text) => {
    if (!text) return '';
    
    return text
      // Bold text **text**
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic text *text*
      .replace(/\*([^*]+)\*/g, '<em>$1</em>')
      // Part numbers (highlighted)
      .replace(/\b(PS\d+|W\d+|WP\w+)\b/g, '<span class="part-number-highlight">$1</span>')
      // Prices
      .replace(/\$(\d+\.\d{2})/g, '<span class="price-highlight">$$1</span>');
  };

  // Parse message for product information
  const parseMessage = (text) => {
    // TODO: Implement parsing logic to extract product data from text
    // Example patterns to look for:
    // - Part numbers: /part number: ([A-Z0-9]+)/i
    // - Prices: /\$(\d+\.\d{2})/
    
    // For now, return text as is
    // In a real implementation, you'd parse and extract structured data
    return { text, products: [] };
  };

  const { text, products } = parseMessage(message.text);

  return (
    <article 
      className={`message ${message.sender}`}
      role="article"
      aria-label={`${message.sender === 'user' ? 'Your' : 'Assistant'} message from ${formatTimestamp(message.timestamp)}`}
    >
      <header className="message-header">
        <span className="sender-name">
          {message.sender === 'user' ? 'You' : 'PartSelect Assistant'}
        </span>
        <time 
          className="timestamp" 
          dateTime={message.timestamp}
          title={new Date(message.timestamp).toLocaleString()}
        >
          {formatTimestamp(message.timestamp)}
        </time>
      </header>
      
      <div 
        className="message-content"
        aria-live={isLatest ? "polite" : "off"}
      >
        {message.error && (
          <div className="error-indicator" role="alert" aria-live="assertive">
            ⚠️ Error
          </div>
        )}
        {message.outOfScope && (
          <div className="out-of-scope-indicator" role="status">
            ℹ️ Out of scope request
          </div>
        )}
        <div className="formatted-message">
          {formatText(text)}
        </div>
        {products.map((product, index) => (
          <ProductCard key={index} product={product} />
        ))}
      </div>
    </article>
  );
});

// Add display name for debugging
Message.displayName = 'Message';

export default Message;