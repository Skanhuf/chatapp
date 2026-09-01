package repository

import (
	"chatapp/internal/model"
	"database/sql"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type ChatRepository struct {
	db *sql.DB
}

func NewChatRepository(db *sql.DB) *ChatRepository {
	return &ChatRepository{db: db}
}

func (r *ChatRepository) Create(chat *model.Chat) error {
	query := `INSERT INTO chats (name, type, created_by) VALUES (?, ?, ?)`
	result, err := r.db.Exec(query, chat.Name, chat.Type, chat.CreatedBy)
	if err != nil {
		return err
	}
	id, _ := result.LastInsertId()
	chat.ID = int(id)
	chat.CreatedAt = time.Now()
	return nil
}

func (r *ChatRepository) GetByUserID(userID int) ([]*model.Chat, error) {
	query := `
		SELECT c.id, c.name, c.type, c.created_by, c.created_at 
		FROM chats c
		JOIN chat_members cm ON c.id = cm.chat_id
		WHERE cm.user_id = ?`
	rows, err := r.db.Query(query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var chats []*model.Chat
	for rows.Next() {
		chat := &model.Chat{}
		rows.Scan(&chat.ID, &chat.Name, &chat.Type, &chat.CreatedBy, &chat.CreatedAt)
		chats = append(chats, chat)
	}
	return chats, nil
}

func (r *ChatRepository) GetMembers(chatID int) ([]*model.User, error) {
	query := `
		SELECT u.id, u.username, u.email, u.status, u.created_at
		FROM users u
		JOIN chat_members cm ON u.id = cm.user_id
		WHERE cm.chat_id = ?`
	rows, err := r.db.Query(query, chatID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var users []*model.User
	for rows.Next() {
		user := &model.User{}
		rows.Scan(&user.ID, &user.Username, &user.Email, &user.Status, &user.CreatedAt)
		users = append(users, user)
	}
	return users, nil
}

func (r *ChatRepository) AddMember(chatID, userID int, role string) error {
	_, err := r.db.Exec("INSERT INTO chat_members (chat_id, user_id, role) VALUES (?, ?, ?)", chatID, userID, role)
	return err
}

func (r *ChatRepository) RemoveMember(chatID, userID int) error {
	_, err := r.db.Exec("DELETE FROM chat_members WHERE chat_id = ? AND user_id = ?", chatID, userID)
	return err
}

func (r *ChatRepository) CreateDirectChat(user1ID, user2ID int) (int, error) {
	tx, _ := r.db.Begin()
	
	// Create chat
	result, err := tx.Exec("INSERT INTO chats (name, type, created_by) VALUES (?, 'direct', ?)", "Direct", user1ID)
	if err != nil {
		tx.Rollback()
		return 0, err
	}
	chatID, _ := result.LastInsertId()
	
	// Add members
	tx.Exec("INSERT INTO chat_members (chat_id, user_id, role) VALUES (?, ?, 'admin')", chatID, user1ID)
	tx.Exec("INSERT INTO chat_members (chat_id, user_id, role) VALUES (?, ?, 'admin')", chatID, user2ID)
	
	tx.Commit()
	return int(chatID), nil
}
