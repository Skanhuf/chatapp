package model

import "time"

type User struct {
	ID           int       `json:"id"`
	Username     string    `json:"username"`
	Email        string    `json:"email"`
	PasswordHash string    `json:"-"`
	Status       string    `json:"status"` // pending, approved, blocked
	CreatedAt    time.Time `json:"created_at"`
}

type Chat struct {
	ID        int       `json:"id"`
	Name      string    `json:"name"`
	Type      string    `json:"type"` // group, direct
	CreatedBy int       `json:"created_by"`
	CreatedAt time.Time `json:"created_at"`
}

type ChatMember struct {
	ChatID int    `json:"chat_id"`
	UserID int    `json:"user_id"`
	Role   string `json:"role"` // admin, member
}

type Message struct {
	ID        int       `json:"id"`
	ChatID    int       `json:"chat_id"`
	UserID    int       `json:"user_id"`
	Content   string    `json:"content"`
	FileURL   string    `json:"file_url,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	Username  string    `json:"username"`
}
