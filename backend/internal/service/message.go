package service

import (
	"chatapp/internal/model"
	"chatapp/internal/repository"
)

type MessageService struct {
	msgRepo  *repository.MessageRepository
	chatRepo *repository.ChatRepository
}

func NewMessageService(msgRepo *repository.MessageRepository, chatRepo *repository.ChatRepository) *MessageService {
	return &MessageService{msgRepo: msgRepo, chatRepo: chatRepo}
}

func (s *MessageService) SendMessage(msg *model.Message) error {
	return s.msgRepo.Save(msg)
}

func (s *MessageService) GetMessages(chatID int, limit, offset int) ([]*model.Message, error) {
	return s.msgRepo.GetByChatID(chatID, limit, offset)
}

func (s *MessageService) SearchMessages(chatID int, q string) ([]*model.Message, error) {
	return s.msgRepo.Search(chatID, q)
}
