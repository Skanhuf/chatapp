package handler

import (
	"chatapp/internal/service"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type ChatHandler struct {
	chatService   *service.ChatService
	messageService *service.MessageService
	userRepo       interface {
		GetPending() ([]*User, error)
		Approve(id int) error
		Block(id int) error
	}
}

func NewChatHandler(chatService *service.ChatService, messageService *service.MessageService, userRepo interface {
	GetPending() ([]*User, error)
	Approve(id int) error
	Block(id int) error
}) *ChatHandler {
	return &ChatHandler{
		chatService:    chatService,
		messageService: messageService,
		userRepo:       userRepo,
	}
}

type CreateChatRequest struct {
	Name       string `json:"name" binding:"required"`
	MemberIDs  []int  `json:"member_ids"`
}

func (h *ChatHandler) GetChats(c *gin.Context) {
	userID := c.GetInt("user_id")
	chats, err := h.chatService.GetChats(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, chats)
}

func (h *ChatHandler) CreateChat(c *gin.Context) {
	userID := c.GetInt("user_id")
	var req CreateChatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	chat, err := h.chatService.CreateChat(req.Name, userID, req.MemberIDs)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusCreated, chat)
}

func (h *ChatHandler) CreateDirectChat(c *gin.Context) {
	userID := c.GetInt("user_id")
	var req struct {
		ParticipantID int `json:"participant_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	chatID, err := h.chatService.CreateDirectChat(userID, req.ParticipantID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusCreated, gin.H{"chat_id": chatID})
}

func (h *ChatHandler) GetChatMembers(c *gin.Context) {
	chatID, _ := strconv.Atoi(c.Param("id"))
	members, err := h.chatService.GetMembers(chatID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, members)
}

func (h *ChatHandler) AddMember(c *gin.Context) {
	chatID, _ := strconv.Atoi(c.Param("id"))
	var req struct {
		UserID int `json:"user_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if err := h.chatService.AddMember(chatID, req.UserID); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "Member added"})
}

func (h *ChatHandler) GetPendingUsers(c *gin.Context) {
	users, err := h.userRepo.GetPending()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, users)
}

func (h *ChatHandler) ApproveUser(c *gin.Context) {
	id, _ := strconv.Atoi(c.Param("id"))
	if err := h.userRepo.Approve(id); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "User approved"})
}

func (h *ChatHandler) BlockUser(c *gin.Context) {
	id, _ := strconv.Atoi(c.Param("id"))
	if err := h.userRepo.Block(id); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "User blocked"})
}
