import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function AdminPanel() {
  const [pendingUsers, setPendingUsers] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    fetchPendingUsers()
  }, [])

  const fetchPendingUsers = async () => {
    const res = await api.get('/admin/users')
    setPendingUsers(res.data)
  }

  const approveUser = async (id) => {
    await api.put(`/admin/users/${id}/approve`)
    fetchPendingUsers()
  }

  const blockUser = async (id) => {
    await api.put(`/admin/users/${id}/block`)
    fetchPendingUsers()
  }

  return (
    <div className="container" style={{ maxWidth: '600px', marginTop: '50px' }}>
      <h2 style={{ marginBottom: '20px' }}>Admin Panel - Pending Users</h2>
      {pendingUsers.length === 0 ? (
        <p>No pending users</p>
      ) : (
        pendingUsers.map(user => (
          <div key={user.id} style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '15px',
            background: 'white',
            borderRadius: '8px',
            marginBottom: '10px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <div>
              <strong>{user.username}</strong>
              <p style={{ fontSize: '12px', color: '#666' }}>{user.email}</p>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={() => approveUser(user.id)} style={{ background: '#27ae60', color: 'white' }}>
                Approve
              </button>
              <button onClick={() => blockUser(user.id)} style={{ background: '#e74c3c', color: 'white' }}>
                Block
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
