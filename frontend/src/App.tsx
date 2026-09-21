import './App.css'
import { useState } from 'react'
import type { FormEvent } from 'react'

const RECOMMENDATIONS = [
  { icon: '📈', title: 'Today’s key signals', text: "Analyze today's Indian stock market using NIFTY 50 (^NSEI) and Sensex (^BSESN) signals" },
  { icon: '📊', title: 'Market segments', text: 'Analyse conditions of large, mid and small cap stocks in the Indian market' },
  { icon: '📰', title: 'Market events', text: 'Track major stock market events shaping investor sentiment' },
  { icon: '🌍', title: 'Global impact', text: 'How global news connects with Indian market movements' },
]

type Message = {
  role: 'user' | 'assistant'
  content: string
}

const API_URL = import.meta.env.VITE_API_URL || '/api/chat'

async function readStream(response: Response, onText: (text: string) => void) {
  if (!response.body) {
    throw new Error('The server returned an empty response.')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (value) {
      onText(decoder.decode(value, { stream: !done }))
    }
    if (done) break
  }
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const sendMessage = async (content: string) => {
    const prompt = content.trim()
    if (!prompt || isLoading) return

    setInput('')
    setError('')
    setMessages((current) => [...current, { role: 'user', content: prompt }])
    setIsLoading(true)

    const assistantIndex = messages.length + 1
    setMessages((current) => [...current, { role: 'assistant', content: '' }])

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: {
            content: prompt,
            id: crypto.randomUUID(),
            role: 'user',
          },
          threadId: crypto.randomUUID(),
          responseId: crypto.randomUUID(),
        }),
      })

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}.`)
      }

      await readStream(response, (text) => {
        setMessages((current) =>
          current.map((message, index) =>
            index === assistantIndex
              ? { ...message, content: message.content + text }
              : message,
          ),
        )
      })
    } catch (requestError) {
      const message = requestError instanceof Error
        ? requestError.message
        : 'Unable to generate a response.'
      setError(message)
      setMessages((current) =>
        current.filter((_, index) => index !== assistantIndex),
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    void sendMessage(input)
  }

  return (
    <main className="app-container">
      <aside className="sidebar">
        <div className="brand">
          <img src="/icon.png" alt="" className="chat-logo" />
          <div>
            <strong>Market Insight</strong>
            <span>AI market intelligence</span>
          </div>
        </div>
        <button className="new-chat" onClick={() => { setMessages([]); setError('') }}>
          <span>＋</span> New analysis
        </button>
        <div className="sidebar-note">
          <span className="status-dot" />
          Local AI assistant online
        </div>
        <p className="sidebar-footer">Powered by Yahoo Finance data</p>
      </aside>

      <div className="chat-panel">
        <header className="chat-header">
          <div>
            <span className="eyebrow">MARKET RESEARCH ASSISTANT</span>
            <h1>Understand the market with confidence</h1>
          </div>
          <div className="live-badge"><span className="status-dot" /> Live analysis</div>
        </header>

        <section className="chat-content" aria-live="polite">
        {messages.length === 0 && (
          <div className="welcome">
            <div className="welcome-icon">✦</div>
            <p className="eyebrow">GOOD MORNING, INVESTOR</p>
            <h2>What would you like to explore?</h2>
            <p className="welcome-copy">Get clear, data-backed insights on Indian stocks, indices, and market trends.</p>
            <div className="recommendations-container">
              {RECOMMENDATIONS.map((recommendation) => (
                <button
                  className="recommendation-box"
                  key={recommendation.text}
                  onClick={() => void sendMessage(recommendation.text)}
                  disabled={isLoading}
                >
                  <span className="recommendation-icon">{recommendation.icon}</span>
                  <span><strong>{recommendation.title}</strong><small>{recommendation.text}</small></span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <article className={`message message-${message.role}`} key={`${message.role}-${index}`}>
            <strong>{message.role === 'user' ? 'You' : 'Market Insight'}</strong>
            <p>{message.content || (isLoading ? 'Analyzing market data…' : '')}</p>
          </article>
        ))}
        </section>

        {error && <p className="chat-error">{error}</p>}

        <form className="chat-form" onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about stocks, indices, or market trends..."
            disabled={isLoading}
            rows={1}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? 'Analyzing…' : 'Send  ↑'}
          </button>
        </form>
      </div>
    </main>
  )
}

export default App
