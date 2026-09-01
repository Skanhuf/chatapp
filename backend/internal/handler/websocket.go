package handler

import (
	"chatapp/internal/model"
	"chatapp/internal/service"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

type WSClient struct {
	conn   *websocket.Conn
	send   chan []byte
	userID int
}

type WSHub struct {
	clients    map[int]*WSClient
	broadcast  chan []byte
	register   chan *WSClient
	unregister chan *WSClient
}

func NewWSHub() *WSHub {
	return &WSHub{
		clients:    make(map[int]*WSClient),
		broadcast:  make(chan []byte),
		register:   make(chan *WSClient),
		unregister: make(chan *WSClient),
	}
}

func (h *WSHub) Run() {
	for {
		select {
		case client := <-h.register:
			h.clients[client.userID] = client
		case client := <-h.unregister:
			if _, ok := h.clients[client.userID]; ok {
				delete(h.clients, client.userID)
				close(client.send)
			}
		case message := <-h.broadcast:
			for _, client := range h.clients {
				select {
				case client.send <- message:
				default:
					close(client.send)
					delete(h.clients, client.userID)
				}
			}
		}
	}
}

type WebSocketHandler struct {
	hub            *WSHub
	chatService    *service.ChatService
	messageService *service.MessageService
}

func NewWebSocketHandler(chatService *service.ChatService, messageService *service.MessageService, userRepo interface{}) *WebSocketHandler {
	hub := NewWSHub()
	go hub.Run() // Start hub in background
	return &WebSocketHandler{
		hub:            hub,
		chatService:    chatService,
		messageService: messageService,
	}
}

func (h *WebSocketHandler) ServeWebSocket(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		return
	}

	// Get user ID from query
	userIDStr := c.Query("userId")
	userID, err := strconv.Atoi(userIDStr)
	if err != nil || userID == 0 {
		conn.Close()
		return
	}

	client := &WSClient{
		conn:   conn,
		send:   make(chan []byte, 256),
		userID: userID,
	}

	h.hub.register <- client
	go h.writePump(client)
	go h.readPump(client)
}

func (h *WebSocketHandler) writePump(client *WSClient) {
	defer client.conn.Close()
	for {
		message, ok := <-client.send
		if !ok {
			client.conn.WriteMessage(websocket.CloseMessage, []byte{})
			return
		}
		client.conn.WriteMessage(websocket.TextMessage, message)
	}
}

func (h *WebSocketHandler) readPump(client *WSClient) {
	defer func() {
		h.hub.unregister <- client
		client.conn.Close()
	}()

	for {
		_, message, err := client.conn.ReadMessage()
		if err != nil {
			break
		}

		var msg struct {
			Type    string `json:"type"`
			ChatID  int    `json:"chat_id"`
			Content string `json:"content"`
		}
		if err := json.Unmarshal(message, &msg); err != nil {
			continue
		}

		if msg.Type == "message" {
			m := &model.Message{
				ChatID:  msg.ChatID,
				UserID:  client.userID,
				Content: msg.Content,
			}
			h.messageService.SendMessage(m)
			m.CreatedAt = time.Now()

			// Get username
			user, _ := h.chatService.GetUserByID(client.userID)
			if user != nil {
				m.Username = user.Username
			}

			data, _ := json.Marshal(m)
			h.hub.broadcast <- data
		}
	}
}
