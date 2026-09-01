import { useState, useEffect, useRef, useCallback } from 'react'
import api from '../services/api'

export default function ChatWindow({ chat, ws, currentUserId }) {
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [members, setMembers] = useState([])
  const [typingUsers, setTypingUsers] = useState([])
  const messagesEndRef = useRef(null)
  const wsRef = useRef(ws)

  // Keep wsRef updated
  useEffect(() => {
    wsRef.current = ws
  }, [ws])

  useEffect(() => {
    fetchMessages()
    fetchMembers()
  }, [chat.id])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Listen for WebSocket messages in real-time
  useEffect(() => {
    if (!wsRef.current) return

    const handleWsMessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        console.log('WS message received:', msg)

        // Если сообщение для этого чата — добавляем
        if (msg.chat_id === chat.id) {
          setMessages(prev => {
            // Проверяем, нет ли уже такого сообщения
            const exists = prev.some(m => m.id === msg.id)
            if (exists) return prev
            return [...prev, msg]
          })
        }
      } catch (e) {
        console.log('Error parsing WS message:', e)
      }
    }

    wsRef.current.onmessage = handleWsMessage

    return () => {
      wsRef.current.onmessage = null
    }
  }, [chat.id])

  const fetchMessages = async () => {
    try {
      const res = await api.get(`/messages/${chat.id}?limit=50`)
      setMessages(res.data || [])
    } catch (e) {
      console.log('Error fetching messages:', e)
    }
  }

  const fetchMembers = async () => {
    try {
      const res = await api.get(`/chats/${chat.id}/members`)
      setMembers(res.data || [])
    } catch (e) {
      console.log('Error fetching members:', e)
    }
  }

  const sendMessage = async () => {
    if (!newMessage.trim()) return

    const content = newMessage.trim()
    setNewMessage('')

    // Отправляем через WebSocket (real-time)
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify({
          type: 'message',
          chat_id: chat.id,
          content: content
        }))
      } catch (e) {
        console.log('WebSocket send failed, falling back to API')
        await saveMessageViaAPI(content)
      }
    } else {
      // Если WS не подключён — отправляем через API
      await saveMessageViaAPI(content)
    }
  }

  const saveMessageViaAPI = async (content) => {
    try {
      await api.post('/messages', {
        chat_id: chat.id,
        content: content
      })
      // Перезагружаем сообщения после отправки через API
      fetchMessages()
    } catch (e) {
      console.log('Error sending message:', e)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Форматирование времени
  const formatTime = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <div style={{
        padding: '15px',
        borderBottom: '1px solid #ddd',
        background: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h3 style={{ margin: 0 }}>{chat.name}</h3>
          <p style={{ fontSize: '12px', color: '#666', margin: '4px 0 0' }}>
            {members.length} {members.length === 1 ? 'member' : 'members'}
          </p>
        </div>
        {/* WebSocket connection indicator */}
        {ws && ws.readyState === WebSocket.OPEN && (
          <span style={{
            fontSize: '11px',
            color: '#27ae60',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <span style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: '#27ae60'
            }} />
            Live
          </span>
        )}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'auto', padding: '15px', background: '#f5f5f5' }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#999', marginTop: '50px' }}>
            No messages yet. Start the conversation!
          </div>
        ) : (
          messages.map(msg => {
            const isOwn = currentUserId && msg.user_id === currentUserId
            return (
              <div key={msg.id} style={{
                marginBottom: '12px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: isOwn ? 'flex-end' : 'flex-start'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: '11px',
                  color: '#999',
                  marginBottom: '4px',
                  padding: '0 10px'
                }}>
                  <strong>{msg.username || 'Unknown'}</strong>
                  <span>{formatTime(msg.created_at)}</span>
                </div>
                <div style={{
                  background: isOwn ? '#4a90d9' : 'white',
                  color: isOwn ? 'white' : '#333',
                  padding: '10px 15px',
                  borderRadius: '12px',
                  borderBottomLeftRadius: isOwn ? '4px' : '12px',
                  borderBottomRightRadius: isOwn ? '12px' : '4px',
                  maxWidth: '70%',
                  wordBreak: 'break-word',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
                }}>
                  {msg.content}
                </div>
              </div>
            )
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Typing indicator */}
      {typingUsers.length > 0 && (
        <div style={{
          padding: '5px 15px',
          fontSize: '12px',
          color: '#999',
          fontStyle: 'italic'
        }}>
          {typingUsers.join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...
        </div>
      )}

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
          onKeyDown={handleKeyPress}
          style={{
            flex: 1,
            padding: '10px 15px',
            border: '1px solid #ddd',
            borderRadius: '20px',
            fontSize: '14px',
            outline: 'none'
          }}
        />
        <button
          onClick={sendMessage}
          disabled={!newMessage.trim()}
          style={{
            background: newMessage.trim() ? '#4a90d9' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '20px',
            padding: '10px 20px',
            fontSize: '14px',
            cursor: newMessage.trim() ? 'pointer' : 'not-allowed',
            fontWeight: 'bold'
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}
