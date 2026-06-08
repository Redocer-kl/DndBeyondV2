package main

import (
	"fmt"
	"log"
	"os"
	"dndbeyondv2/dndbackend/config"
	"dndbeyondv2/dndbackend/handlers"
	"dndbeyondv2/dndbackend/middleware"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	// Загружаем .env
	if err := godotenv.Load(); err != nil {
		log.Println("Предупреждение: .env файл не найден")
	}

	// Подключаем базу данных
	config.ConnectDatabase()

	// Инициализируем Gin
	r := gin.Default()

	// Публичные роуты (Auth)
	authGroup := r.Group("/api/auth")
	{
		authGroup.POST("/register", handlers.Register)
		authGroup.POST("/login", handlers.Login)
		authGroup.POST("/logout", handlers.Logout)
	}

	// Защищенные роуты (Требуют JWT)
	protectedGroup := r.Group("/api")
	protectedGroup.Use(middleware.AuthMiddleware())
	{
		protectedGroup.GET("/profile", handlers.GetProfile)
		protectedGroup.GET("/characters", handlers.GetUserCharacters)
		protectedGroup.PUT("/characters/:id", handlers.UpdateCharacter)
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	fmt.Printf("🚀 Основной бэкенд запущен на порту %s\n", port)
	r.Run(":" + port)
}