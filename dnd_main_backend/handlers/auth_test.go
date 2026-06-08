package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"dndbeyondv2/dndbackend/config"
	"dndbeyondv2/dndbackend/models"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// Вспомогательная функция для настройки чистого Gin и SQLite в памяти
func setupTestEnv() *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.Default()

	// Подключаем временную БД в памяти
	db, _ := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	db.AutoMigrate(&models.User{}, &models.Character{})
	config.DB = db

	os.Setenv("JWT_SECRET", "test_secret_key_2026")
	return r
}

func TestRegister_Success(t *testing.T) {
	r := setupTestEnv()
	r.POST("/api/auth/register", Register)

	// Подготавливаем JSON с данными пользователя
	input := RegisterInput{
		Username: "testuser",
		Email:    "test@frog.com",
		Password: "password123",
	}
	jsonValue, _ := json.Marshal(input)

	// Имитируем HTTP запрос
	req, _ := http.NewRequest("POST", "/api/auth/register", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")
	
	w := httptest.NewRecorder() // Сюда запишется ответ сервера
	r.ServeHTTP(w, req)

	// Проверяем статус ответа (Ожидаем 201 Created)
	if w.Code != http.StatusCreated {
		t.Errorf("Ожидался статус 201, получили %d", w.Code)
	}

	// Проверяем, что в ответе пришел токен
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)

	if response["status"] != "success" || response["token"] == "" {
		t.Errorf("Запрос регистрации вернул некорректный ответ: %v", w.Body.String())
	}
}

func TestRegister_ValidationError(t *testing.T) {
	r := setupTestEnv()
	r.POST("/api/auth/register", Register)

	// Передаем некорректный email и слишком короткий пароль
	input := RegisterInput{
		Username: "baduser",
		Email:    "not-an-email", 
		Password: "123",
	}
	jsonValue, _ := json.Marshal(input)

	req, _ := http.NewRequest("POST", "/api/auth/register", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")
	
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	// Ожидаем 400 Bad Request
	if w.Code != http.StatusBadRequest {
		t.Errorf("Ожидался статус 400 при невалидных данных, получили %d", w.Code)
	}
}