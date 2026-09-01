package service

import (
	"chatapp/internal/model"
	"chatapp/internal/repository"
	"errors"

	"golang.org/x/crypto/bcrypt"
)

type AuthService struct {
	userRepo *repository.UserRepository
}

func NewAuthService(userRepo *repository.UserRepository) *AuthService {
	return &AuthService{userRepo: userRepo}
}

func (s *AuthService) Register(username, email, password string) (*model.User, error) {
	if len(username) < 3 || len(password) < 6 {
		return nil, errors.New("username must be at least 3 characters, password at least 6")
	}

	existing, err := s.userRepo.FindByUsername(username)
	if err == nil && existing != nil {
		return nil, errors.New("username already taken")
	}

	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	user := &model.User{
		Username:     username,
		Email:        email,
		PasswordHash: string(hash),
		Status:       "pending",
	}

	err = s.userRepo.Create(user)
	return user, err
}

func (s *AuthService) Login(username, password string) (*model.User, error) {
	user, err := s.userRepo.FindByUsername(username)
	if err != nil {
		return nil, errors.New("invalid credentials")
	}

	if user.Status != "approved" {
		return nil, errors.New("account not approved")
	}

	err = bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(password))
	if err != nil {
		return nil, errors.New("invalid credentials")
	}

	return user, nil
}

func (s *AuthService) GetProfile(id int) (*model.User, error) {
	return s.userRepo.FindByID(id)
}

func (s *AuthService) UpdateProfile(id int, email string) error {
	return s.userRepo.UpdateProfile(id, email)
}

func (s *AuthService) SearchUsers(q string) ([]*model.User, error) {
	return s.userRepo.Search(q)
}
