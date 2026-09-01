package repository

import (
	"chatapp/internal/model"
	"database/sql"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

func NewDatabase(path string) (*sql.DB, error) {
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		return nil, err
	}

	// Create tables
	db.Exec(`CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE NOT NULL,
		email TEXT NOT NULL,
		password_hash TEXT NOT NULL,
		status TEXT NOT NULL DEFAULT 'pending',
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	)`)

	db.Exec(`CREATE TABLE IF NOT EXISTS chats (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		type TEXT NOT NULL,
		created_by INTEGER NOT NULL,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	)`)

	db.Exec(`CREATE TABLE IF NOT EXISTS chat_members (
		chat_id INTEGER NOT NULL,
		user_id INTEGER NOT NULL,
		role TEXT NOT NULL DEFAULT 'member',
		PRIMARY KEY (chat_id, user_id)
	)`)

	db.Exec(`CREATE TABLE IF NOT EXISTS messages (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		chat_id INTEGER NOT NULL,
		user_id INTEGER NOT NULL,
		content TEXT NOT NULL,
		file_url TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	)`)

	return db, nil
}

type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) Create(user *model.User) error {
	query := `INSERT INTO users (username, email, password_hash, status) VALUES (?, ?, ?, 'pending')`
	result, err := r.db.Exec(query, user.Username, user.Email, user.PasswordHash)
	if err != nil {
		return err
	}
	id, _ := result.LastInsertId()
	user.ID = int(id)
	user.CreatedAt = time.Now()
	return nil
}

func (r *UserRepository)FindByUsername(username string) (*model.User, error) {
	user := &model.User{}
	err := r.db.QueryRow("SELECT id, username, email, password_hash, status, created_at FROM users WHERE username = ?", username).
		Scan(&user.ID, &user.Username, &user.Email, &user.PasswordHash, &user.Status, &user.CreatedAt)
	if err != nil {
		return nil, err
	}
	return user, nil
}

func (r *UserRepository) FindByID(id int) (*model.User, error) {
	user := &model.User{}
	err := r.db.QueryRow("SELECT id, username, email, password_hash, status, created_at FROM users WHERE id = ?", id).
		Scan(&user.ID, &user.Username, &user.Email, &user.PasswordHash, &user.Status, &user.CreatedAt)
	if err != nil {
		return nil, err
	}
	return user, nil
}

func (r *UserRepository) GetAllApproved() ([]*model.User, error) {
	rows, err := r.db.Query("SELECT id, username, email, status, created_at FROM users WHERE status = 'approved'")
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

func (r *UserRepository) GetPending() ([]*model.User, error) {
	rows, err := r.db.Query("SELECT id, username, email, status, created_at FROM users WHERE status = 'pending'")
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

func (r *UserRepository) Approve(id int) error {
	_, err := r.db.Exec("UPDATE users SET status = 'approved' WHERE id = ?", id)
	return err
}

func (r *UserRepository) Block(id int) error {
	_, err := r.db.Exec("UPDATE users SET status = 'blocked' WHERE id = ?", id)
	return err
}

func (r *UserRepository) Search(q string) ([]*model.User, error) {
	rows, err := r.db.Query("SELECT id, username, email, status, created_at FROM users WHERE username LIKE ? AND status = 'approved'", "%"+q+"%")
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

func (r *UserRepository) UpdateProfile(id int, email string) error {
	_, err := r.db.Exec("UPDATE users SET email = ? WHERE id = ?", email, id)
	return err
}
