import { useState, useEffect, useRef } from 'react'
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
  const [selectedUsers, setSelectedUsers] = useState([])
  const wsRef = useRef(null)

  if (!user) return <div style={{padding: '50px', textAlign: 'center'}}>Loading...</div>

  useEffect(() => {
    fetchChats()
    fetchUsers()
    connectWebSocket()
    return () => {
      if (wsRef.current) wsRef.current.close()
    }
  }, [])

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(`ws://${window.location.host}/ws?userId=${user.id}`)
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data)
        if (msg.type === 'message') {
          setChats(prev => prev.map(chat =>
            chat.id === msg.chat_id
              ? { ...chat, lastMessage: msg.content }
              : chat
          ))
        }
      }
      ws.onerror = () => console.log('WebSocket error')
      wsRef.current = ws
    } catch (e) {
      console.log('WebSocket not available')
    }
  }

  const fetchChats = async () => {
    const res = await api.get('/chats')
    setChats(res.data)
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
    await api.post('/chats', {
      name: newChatName,
      member_ids: selectedUsers
    })
    setNewChatName('')
    setSelectedUsers([])
    setShowCreate(false)
    fetchChats()
  }

  const createDirectChat = async (userId) => {
    await api.post('/chats/direct', { participant_id: userId })
    fetchChats()
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
        <div style={{ padding: '15px', borderBottom: '1px solid #ddd' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>ChatApp</h3>
            <button onClick={logout} style={{ background: '#e74c3c', color: 'white', padding: '5px 10px', fontSize: '12px' }}>
              Logout
            </button>
          </div>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>{user.username}</p>
        </div>

        <div style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>
          <button
            onClick={() => setShowCreate(!showCreate)}
            style={{ background: '#4a90d9', color: 'white', width: '100%' }}
          >
            {showCreate ? 'Cancel' : '+ New Chat'}
          </button>
        </div>

        {showCreate && (
          <div style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>
            <input
              type="text"
              placeholder="Chat name"
              value={newChatName}
              onChange={e => setNewChatName(e.target.value)}
              style={{ marginBottom: '10px' }}
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

        <div style={{ flex: 1, overflow: 'auto' }}>
          {chats.map(chat => (
            <div
              key={chat.id}
              onClick={() => setSelectedChat(chat)}
              style={{
                padding: '12px 15px',
                cursor: 'pointer',
                background: selectedChat?.id === chat.id ? '#e8f4fd' : 'transparent',
                borderBottom: '1px solid #eee'
              }}
            >
              <strong>{chat.name}</strong>
              <p style={{ fontSize: '12px', color: '#666' }}>{chat.type}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {selectedChat ? (
          <ChatWindow chat={selectedChat} ws={wsRef.current} />
        ) : (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
            Select a chat
          </div>
        )}
      </div>
    </div>
  )
}
