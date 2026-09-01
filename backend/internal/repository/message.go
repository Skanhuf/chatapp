package repository

import (
	"chatapp/internal/model"
	"database/sql"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type MessageRepository struct {
	db *sql.DB
}

func NewMessageRepository(db *sql.DB) *MessageRepository {
	return &MessageRepository{db: db}
}

func (r *MessageRepository) Save(msg *model.Message) error {
	query := `INSERT INTO messages (chat_id, user_id, content, file_url) VALUES (?, ?, ?, ?)`
	result, err := r.db.Exec(query, msg.ChatID, msg.UserID, msg.Content, msg.FileURL)
	if err != nil {
		return err
	}
	id, _ := result.LastInsertId()
	msg.ID = int(id)
	msg.CreatedAt = time.Now()
	return nil
}

func (r *MessageRepository) GetByChatID(chatID int, limit, offset int) ([]*model.Message, error) {
	query := `
		SELECT m.id, m.chat_id, m.user_id, m.content, m.file_url, m.created_at, u.username
		FROM messages m
		JOIN users u ON m.user_id = u.id
		WHERE m.chat_id = ?
		ORDER BY m.created_at DESC
		LIMIT ? OFFSET ?`
	rows, err := r.db.Query(query, chatID, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var messages []*model.Message
	for rows.Next() {
		msg := &model.Message{}
		rows.Scan(&msg.ID, &msg.ChatID, &msg.UserID, &msg.Content, &msg.FileURL, &msg.CreatedAt, &msg.Username)
		messages = append(messages, msg)
	}
	// Reverse to get oldest first
	for i, j := 0, len(messages)-1; i < j; i, j = i+1, j-1 {
		messages[i], messages[j] = messages[j], messages[i]
	}
	return messages, nil
}

func (r *MessageRepository) Search(chatID int, q string) ([]*model.Message, error) {
	query := `
		SELECT m.id, m.chat_id, m.user_id, m.content, m.file_url, m.created_at, u.username
		FROM messages m
		JOIN users u ON m.user_id = u.id
		WHERE m.chat_id = ? AND m.content LIKE ?
		ORDER BY m.created_at DESC`
	rows, err := r.db.Query(query, chatID, "%"+q+"%")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var messages []*model.Message
	for rows.Next() {
		msg := &model.Message{}
		rows.Scan(&msg.ID, &msg.ChatID, &msg.UserID, &msg.Content, &msg.FileURL, &msg.CreatedAt, &msg.Username)
		messages = append(messages, msg)
	}
	return messages, nil
}
