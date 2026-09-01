import { useState, useEffect, useRef } from 'react'
import api from '../services/api'

export default function ChatWindow({ chat, ws }) {
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [members, setMembers] = useState([])
  const messagesEndRef = useRef(null)

  useEffect(() => {
    fetchMessages()
    fetchMembers()
  }, [chat.id])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchMessages = async () => {
    const res = await api.get(`/messages/${chat.id}?limit=50`)
    setMessages(res.data)
  }

  const fetchMembers = async () => {
    const res = await api.get(`/chats/${chat.id}/members`)
    setMembers(res.data)
  }

  const sendMessage = async () => {
    if (!newMessage.trim()) return

    // Send via WebSocket
    if (ws) {
      ws.send(JSON.stringify({
        type: 'message',
        chat_id: chat.id,
        content: newMessage
      }))
    }

    // Also save via API
    await api.post('/messages', {
      chat_id: chat.id,
      content: newMessage
    })

    setNewMessage('')
    fetchMessages()
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <div style={{
        padding: '15px',
        borderBottom: '1px solid #ddd',
        background: 'white'
      }}>
        <h3>{chat.name}</h3>
        <p style={{ fontSize: '12px', color: '#666' }}>
          {members.length} members
        </p>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'auto', padding: '15px' }}>
        {messages.map(msg => (
          <div key={msg.id} style={{
            marginBottom: '10px',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: '12px',
              color: '#666',
              marginBottom: '2px'
            }}>
              <strong>{msg.username}</strong>
              <span>{new Date(msg.created_at).toLocaleTimeString()}</span>
            </div>
            <div style={{
              background: '#e8f4fd',
              padding: '10px 15px',
              borderRadius: '12px',
              maxWidth: '70%',
              wordBreak: 'break-word'
            }}>
              {msg.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '15px',
        borderTop: '1px solid #ddd',
        background: 'white',
        display: 'flex',
        gap: '10px'
      }}>
        <input
          type="text"
          placeholder="Type a message..."
          value={newMessage}
          onChange={e => setNewMessage(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          style={{ flex: 1 }}
        />
        <button onClick={sendMessage} style={{ background: '#4a90d9', color: 'white' }}>
          Send
        </button>
      </div>
    </div>
  )
}
