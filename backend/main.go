package main

import (
	"log"
	"os"

	"chatapp/internal/handler"
	"chatapp/internal/repository"
	"chatapp/internal/service"

	"github.com/gin-gonic/gin"
)

func main() {
	// Load config
	port := os.Getenv("PORT")
	if port == "" {
		port = "3001"
	}

	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "/data/chat.db"
	}

	// Initialize database
	db, err := repository.NewDatabase(dbPath)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Initialize repositories
	userRepo := repository.NewUserRepository(db)
	chatRepo := repository.NewChatRepository(db)
	messageRepo := repository.NewMessageRepository(db)

	// Initialize services
	authService := service.NewAuthService(userRepo)
	chatService := service.NewChatService(chatRepo, userRepo)
	messageService := service.NewMessageService(messageRepo, chatRepo)

	// Initialize handlers
	authHandler := handler.NewAuthHandler(authService)
	chatHandler := handler.NewChatHandler(chatService, messageService, userRepo)
	messageHandler := handler.NewMessageHandler(messageService)
	wsHandler := handler.NewWebSocketHandler(chatService, messageService, userRepo)

	// Setup router
	router := gin.Default()

	// CORS middleware
	router.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	// API routes
	api := router.Group("/api")
	{
		// Auth
		api.POST("/auth/register", authHandler.Register)
		api.POST("/auth/login", authHandler.Login)
		api.GET("/auth/me", authHandler.GetMe)
		api.PUT("/auth/profile", authHandler.UpdateProfile)
		api.GET("/auth/search", authHandler.SearchUsers)

		// Admin
		api.GET("/admin/users", chatHandler.GetPendingUsers)
		api.PUT("/admin/users/:id/approve", chatHandler.ApproveUser)
		api.PUT("/admin/users/:id/block", chatHandler.BlockUser)

		// Chats
		api.GET("/chats", chatHandler.GetChats)
		api.POST("/chats", chatHandler.CreateChat)
		api.POST("/chats/direct", chatHandler.CreateDirectChat)
		api.POST("/chats/groups", chatHandler.CreateChat)
		api.GET("/chats/:id/members", chatHandler.GetChatMembers)
		api.POST("/chats/:id/members", chatHandler.AddMember)
		api.DELETE("/chats/:id/members/:userId", chatHandler.RemoveMember)
		api.POST("/chats/:id/leave", chatHandler.LeaveChat)

		// Messages
		api.GET("/messages/:chatId", messageHandler.GetMessages)
		api.POST("/messages", messageHandler.SendMessage)
	}

	// WebSocket
	router.GET("/ws", wsHandler.ServeWebSocket)

	log.Printf("Server starting on port %s", port)
	router.Run(":" + port)
}
