package service

import (
	"chatapp/internal/model"
	"chatapp/internal/repository"
)

type ChatService struct {
	chatRepo   *repository.ChatRepository
	userRepo   *repository.UserRepository
}

func NewChatService(chatRepo *repository.ChatRepository, userRepo *repository.UserRepository) *ChatService {
	return &ChatService{chatRepo: chatRepo, userRepo: userRepo}
}

func (s *ChatService) GetChats(userID int) ([]*model.Chat, error) {
	return s.chatRepo.GetByUserID(userID)
}

func (s *ChatService) CreateChat(name string, createdBy int, memberIDs []int) (*model.Chat, error) {
	chat := &model.Chat{
		Name:      name,
		Type:      "group",
		CreatedBy: createdBy,
	}

	err := s.chatRepo.Create(chat)
	if err != nil {
		return nil, err
	}

	// Add creator as admin
	s.chatRepo.AddMember(chat.ID, createdBy, "admin")

	// Add other members
	for _, uid := range memberIDs {
		s.chatRepo.AddMember(chat.ID, uid, "member")
	}

	return chat, nil
}

func (s *ChatService) CreateDirectChat(user1ID, user2ID int) (int, error) {
	return s.chatRepo.CreateDirectChat(user1ID, user2ID)
}

func (s *ChatService) GetMembers(chatID int) ([]*model.User, error) {
	return s.chatRepo.GetMembers(chatID)
}

func (s *ChatService) AddMember(chatID, userID int) error {
	return s.chatRepo.AddMember(chatID, userID, "member")
}

func (s *ChatService) RemoveMember(chatID, userID int) error {
	return s.chatRepo.RemoveMember(chatID, userID)
}

func (s *ChatService) GetUserByID(id int) (*model.User, error) {
	return s.userRepo.FindByID(id)
}
