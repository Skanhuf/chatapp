import { useState, useEffect, useRef, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import ChatWindow from '../components/ChatWindow'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [chats, setChats] = useState([])
  const [selectedChat, setSelectedChat] = useState(null)
  const [newChatName, setNewChatName] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [users, setUsers] = useState([])
  const [wsConnected, setWsConnected] = useState(false)
  const [wsError, setWsError] = useState(false)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  if (!user) return <div style={{padding: '50px', textAlign: 'center'}}>Loading...</div>

  useEffect(() => {
    fetchChats()
    fetchUsers()
    connectWebSocket()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.onopen = null
        wsRef.current.onmessage = null
        wsRef.current.onerror = null
        wsRef.current.onclose = null
        wsRef.current.close()
      }
    }
  }, [])

  const connectWebSocket = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/ws?userId=${user.id}`
      console.log('Connecting to:', wsUrl)

      const ws = new WebSocket(wsUrl)
      ws.onopen = () => {
        console.log('WebSocket connected')
        setWsConnected(true)
        setWsError(false)
      }
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          console.log('Received WS message:', msg)

          // Если это сообщение — добавляем в текущий чат или обновляем список
          if (msg.chat_id === selectedChat?.id) {
            // Проверяем, нет ли уже такого сообщения
            setChats(prev => prev.map(chat => {
              if (chat.id === msg.chat_id) {
                return {
                  ...chat,
                  lastMessage: msg.content,
                  lastMessageTime: msg.created_at
                }
              }
              return chat
            }))
          }

          // Обновляем lastMessage в списке чатов
          setChats(prev => prev.map(chat =>
            chat.id === msg.chat_id
              ? { ...chat, lastMessage: msg.content, lastMessageTime: msg.created_at }
              : chat
          ))
        } catch (e) {
          console.log('Error parsing WS message:', e)
        }
      }
      ws.onerror = (e) => {
        console.log('WebSocket error:', e)
        setWsError(true)
        setWsConnected(false)
      }
      ws.onclose = () => {
        console.log('WebSocket closed, reconnecting in 3s...')
        setWsConnected(false)
        // Автоматическая переподключение
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket()
        }, 3000)
      }
      wsRef.current = ws
    } catch (e) {
      console.log('WebSocket not available:', e)
      setWsError(true)
    }
  }, [user.id, selectedChat])

  const fetchChats = async () => {
    try {
      const res = await api.get('/chats')
      setChats(res.data || [])
    } catch (e) {
      console.log('Error fetching chats:', e)
    }
  }

  const fetchUsers = async () => {
    try {
      const res = await api.get('/auth/search?q=')
      setUsers(res.data || [])
    } catch (e) {
      console.log('Error fetching users:', e)
    }
  }

  const createChat = async () => {
    try {
      await api.post('/chats', {
        name: newChatName,
        member_ids: selectedUsers
      })
      setNewChatName('')
      setSelectedUsers([])
      setShowCreate(false)
      fetchChats()
    } catch (e) {
      console.log('Error creating chat:', e)
    }
  }

  const createDirectChat = async (userId) => {
    try {
      await api.post('/chats/direct', { participant_id: userId })
      fetchChats()
    } catch (e) {
      console.log('Error creating direct chat:', e)
    }
  }

  const handleChatSelect = async (chat) => {
    setSelectedChat(chat)
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar */}
      <div style={{
        width: '300px',
        borderRight: '1px solid #ddd',
        display: 'flex',
        flexDirection: 'column',
        background: 'white'
      }}>
        {/* Header */}
        <div style={{ padding: '15px', borderBottom: '1px solid #ddd' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>ChatApp</h3>
            <button onClick={logout} style={{ background: '#e74c3c', color: 'white', padding: '5px 10px', fontSize: '12px' }}>
              Logout
            </button>
          </div>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>{user.username}</p>
          {/* WebSocket status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '8px', fontSize: '11px' }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: wsConnected ? '#27ae60' : wsError ? '#e74c3c' : '#f39c12'
            }} />
            <span style={{ color: wsConnected ? '#27ae60' : wsError ? '#e74c3c' : '#f39c12' }}>
              {wsConnected ? 'Online' : wsError ? 'Disconnected' : 'Connecting...'}
            </span>
          </div>
        </div>

        {/* New Chat Button */}
        <div style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>
          <button
            onClick={() => setShowCreate(!showCreate)}
            style={{ background: '#4a90d9', color: 'white', width: '100%' }}
          >
            {showCreate ? 'Cancel' : '+ New Chat'}
          </button>
        </div>

        {/* Create Chat Form */}
        {showCreate && (
          <div style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>
            <input
              type="text"
              placeholder="Chat name"
              value={newChatName}
              onChange={e => setNewChatName(e.target.value)}
              style={{ marginBottom: '10px', width: 'calc(100% - 20px)', padding: '8px', boxSizing: 'border-box' }}
            />
            <div style={{ maxHeight: '150px', overflow: 'auto' }}>
              {users.map(u => (
                <label key={u.id} style={{ display: 'block', padding: '5px 0' }}>
                  <input
                    type="checkbox"
                    checked={selectedUsers.includes(u.id)}
                    onChange={e => {
                      if (e.target.checked) {
                        setSelectedUsers([...selectedUsers, u.id])
                      } else {
                        setSelectedUsers(selectedUsers.filter(id => id !== u.id))
                      }
                    }}
                  />
                  {u.username}
                </label>
              ))}
            </div>
            <button onClick={createChat} style={{ background: '#27ae60', color: 'white', width: '100%', marginTop: '10px' }}>
              Create Group
            </button>
          </div>
        )}

        {/* Chat List */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          {chats.map(chat => (
            <div
              key={chat.id}
              onClick={() => handleChatSelect(chat)}
              style={{
                padding: '12px 15px',
                cursor: 'pointer',
                background: selectedChat?.id === chat.id ? '#e8f4fd' : 'transparent',
                borderBottom: '1px solid #eee'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong>{chat.name}</strong>
                <span style={{ fontSize: '10px', color: '#999' }}>
                  {chat.type}
                </span>
              </div>
              {chat.lastMessage && (
                <p style={{ fontSize: '12px', color: '#666', margin: '4px 0 0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {chat.lastMessage}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {selectedChat ? (
          <ChatWindow chat={selectedChat} ws={wsRef.current} currentUserId={user.id} />
        ) : (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>💬</div>
              Select a chat to start messaging
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
