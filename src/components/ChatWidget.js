import React, { useState, useRef, useEffect, useCallback } from 'react';

const API_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : (typeof window !== 'undefined' ? window.CHATBOT_API_URL || 'http://localhost:8000' : 'http://localhost:8000');

// Generate a persistent session ID per browser tab
function getSessionId() {
  if (typeof window === 'undefined') return null;
  let id = sessionStorage.getItem('chatbot_session_id');
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem('chatbot_session_id', id);
  }
  return id;
}

const styles = {
  toggle: {
    position: 'fixed',
    bottom: '24px',
    right: '24px',
    width: '56px',
    height: '56px',
    borderRadius: '50%',
    background: 'var(--ifm-color-primary)',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
  },
  panel: {
    position: 'fixed',
    bottom: '90px',
    right: '24px',
    width: '380px',
    maxHeight: '500px',
    borderRadius: '12px',
    background: 'var(--ifm-background-color)',
    border: '1px solid var(--ifm-color-emphasis-300)',
    display: 'flex',
    flexDirection: 'column',
    zIndex: 1000,
    boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
    overflow: 'hidden',
  },
  header: {
    padding: '12px 16px',
    borderBottom: '1px solid var(--ifm-color-emphasis-200)',
    fontWeight: 600,
    fontSize: '14px',
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '12px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    maxHeight: '340px',
  },
  inputRow: {
    display: 'flex',
    borderTop: '1px solid var(--ifm-color-emphasis-200)',
    padding: '8px',
    gap: '8px',
  },
  input: {
    flex: 1,
    padding: '8px 12px',
    borderRadius: '8px',
    border: '1px solid var(--ifm-color-emphasis-300)',
    background: 'var(--ifm-background-color)',
    color: 'var(--ifm-font-color-base)',
    fontSize: '14px',
    outline: 'none',
  },
  sendBtn: {
    padding: '8px 16px',
    borderRadius: '8px',
    background: 'var(--ifm-color-primary)',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
  },
  userMsg: {
    alignSelf: 'flex-end',
    background: 'var(--ifm-color-primary)',
    color: '#fff',
    padding: '8px 12px',
    borderRadius: '12px 12px 4px 12px',
    maxWidth: '80%',
    fontSize: '14px',
  },
  botMsg: {
    alignSelf: 'flex-start',
    background: 'var(--ifm-color-emphasis-100)',
    padding: '8px 12px',
    borderRadius: '12px 12px 12px 4px',
    maxWidth: '80%',
    fontSize: '14px',
  },
  sources: {
    marginTop: '8px',
    fontSize: '12px',
    color: 'var(--ifm-color-emphasis-600)',
    borderTop: '1px solid var(--ifm-color-emphasis-200)',
    paddingTop: '6px',
  },
  sourceLink: {
    color: 'var(--ifm-color-primary)',
    textDecoration: 'none',
    fontSize: '12px',
  },
  loading: {
    alignSelf: 'flex-start',
    padding: '8px 12px',
    fontSize: '14px',
    color: 'var(--ifm-color-emphasis-500)',
  },
  selectedTextBanner: {
    padding: '8px 12px',
    background: 'var(--ifm-color-primary-lightest, #e8f0fe)',
    borderBottom: '1px solid var(--ifm-color-emphasis-200)',
    fontSize: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '8px',
  },
  selectedTextPreview: {
    flex: 1,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    color: 'var(--ifm-font-color-base)',
  },
  clearBtn: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    color: 'var(--ifm-color-emphasis-600)',
    padding: '2px 6px',
  },
  primaryBadge: {
    display: 'inline-block',
    background: 'var(--ifm-color-primary)',
    color: '#fff',
    fontSize: '10px',
    padding: '1px 5px',
    borderRadius: '4px',
    marginRight: '4px',
  },
};

function sourceToDocPath(source) {
  if (!source || source === 'user-selected') return null;
  let path = source.replace(/^docs\//, '/docs/').replace(/\.md$/, '');
  if (!path.startsWith('/')) path = '/docs/' + path;
  return path;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const messagesEnd = useRef(null);
  const sessionId = useRef(getSessionId());

  // Capture text selection when the chat widget opens
  const captureSelection = useCallback(() => {
    if (typeof window === 'undefined') return;
    const selection = window.getSelection();
    const text = selection ? selection.toString().trim() : '';
    if (text.length >= 20 && text.length <= 5000) {
      setSelectedText(text);
    }
  }, []);

  // When opening the chat, capture any selected text
  const handleToggle = useCallback(() => {
    if (!isOpen) {
      captureSelection();
    }
    setIsOpen(prev => !prev);
  }, [isOpen, captureSelection]);

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async () => {
    const question = input.trim();
    if (!question || loading) return;

    setInput('');
    const currentSelectedText = selectedText;

    // Show user message with selected text indicator
    const userDisplay = currentSelectedText
      ? `[About selected text] ${question}`
      : question;
    setMessages(prev => [...prev, { role: 'user', text: userDisplay }]);
    setLoading(true);

    // Clear selected text after sending
    if (currentSelectedText) setSelectedText('');

    try {
      const body = { question, session_id: sessionId.current };
      if (currentSelectedText) {
        body.selected_text = currentSelectedText;
      }

      const res = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Server error' }));
        setMessages(prev => [...prev, {
          role: 'bot',
          text: err.detail || 'Something went wrong. Please try again.',
          sources: [],
        }]);
      } else {
        const data = await res.json();
        // Update session_id from server if provided
        if (data.session_id) {
          sessionId.current = data.session_id;
          if (typeof window !== 'undefined') {
            sessionStorage.setItem('chatbot_session_id', data.session_id);
          }
        }
        setMessages(prev => [...prev, {
          role: 'bot',
          text: data.answer,
          sources: data.sources || [],
          retrievalMode: data.retrieval_mode,
        }]);
      }
    } catch {
      setMessages(prev => [...prev, {
        role: 'bot',
        text: 'Could not connect to the chatbot server. Make sure the backend is running.',
        sources: [],
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <button
        onClick={handleToggle}
        style={styles.toggle}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? '\u00D7' : '\uD83D\uDCAC'}
      </button>

      {isOpen && (
        <div style={styles.panel}>
          <div style={styles.header}>Ask the Textbook</div>

          {selectedText && (
            <div style={styles.selectedTextBanner}>
              <span style={styles.selectedTextPreview}>
                Selected: &ldquo;{selectedText.substring(0, 80)}
                {selectedText.length > 80 ? '...' : ''}&rdquo;
              </span>
              <button
                style={styles.clearBtn}
                onClick={() => setSelectedText('')}
                aria-label="Clear selection"
              >
                &times;
              </button>
            </div>
          )}

          <div style={styles.messages}>
            {messages.length === 0 && (
              <div style={{ color: 'var(--ifm-color-emphasis-500)', fontSize: '13px' }}>
                Ask a question about the textbook content.
                {!selectedText && ' Highlight text on the page before opening chat to ask about a specific passage.'}
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i}>
                <div style={msg.role === 'user' ? styles.userMsg : styles.botMsg}>
                  {msg.text}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div style={styles.sources}>
                    <strong>Sources:</strong>
                    {msg.sources.map((src, j) => {
                      const docPath = sourceToDocPath(src.source);
                      return (
                        <div key={j}>
                          {src.is_primary && (
                            <span style={styles.primaryBadge}>PRIMARY</span>
                          )}
                          {docPath ? (
                            <a href={docPath} style={styles.sourceLink}>
                              {src.part} &rsaquo; {src.section}
                            </a>
                          ) : (
                            <span>
                              {src.part} &rsaquo; {src.section}
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
            {loading && <div style={styles.loading}>Thinking...</div>}
            <div ref={messagesEnd} />
          </div>
          <div style={styles.inputRow}>
            <input
              style={styles.input}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={selectedText ? 'Ask about the selected text...' : 'Ask about the textbook...'}
              disabled={loading}
            />
            <button
              style={{
                ...styles.sendBtn,
                opacity: loading ? 0.5 : 1,
              }}
              onClick={sendMessage}
              disabled={loading}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}
