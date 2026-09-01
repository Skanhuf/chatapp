package repository

import (
	"chatapp/internal/model"
	"database/sql"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

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
