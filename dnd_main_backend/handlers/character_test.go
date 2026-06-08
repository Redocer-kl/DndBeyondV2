package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"dndbeyondv2/dndbackend/config"
	"dndbeyondv2/dndbackend/middleware"
	"dndbeyondv2/dndbackend/models"

)

func TestUpdateCharacter_ValidationAndAC(t *testing.T) {
	r := setupTestEnv()
	
	// Настраиваем роут с нашей прослойкой авторизации
	r.PUT("/api/characters/:id", middleware.AuthMiddleware(), UpdateCharacter)

	// 1. Создаем тестового пользователя и его персонажа прямо в тестовой БД
	testUser := models.User{Username: "player1", Email: "p1@frog.com", Password: "hashed_password"}
	config.DB.Create(&testUser)

	testChar := models.Character{
		UserID:    testUser.ID,
		Name:      "Старый Плут",
		Level:     1,
		Dexterity: 10,
	}
	config.DB.Create(&testChar)

	// Генерируем реальный JWT для этого пользователя
	token, _ := middleware.GenerateToken(testUser.ID)

	// 2. Тестируем валидацию: Пытаемся поставить Силу = 50 (максимум 30)
	badInput := UpdateCharacterInput{Strength: 50}
	badJson, _ := json.Marshal(badInput)

	req, _ := http.NewRequest("PUT", "/api/characters/1", bytes.NewBuffer(badJson))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")
	
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Ожидался статус 400 для Силы=50, получили %d", w.Code)
	}

	// 3. Тестируем успешное обновление и пересчет AC (Класса Доспеха)
	// Поставим Ловкость = 16 (модификатор должен стать +3, следовательно AC = 10 + 3 = 13)
	goodInput := UpdateCharacterInput{
		Name:      "Алёшка",
		Level:     3,
		Dexterity: 16,
	}
	goodJson, _ := json.Marshal(goodInput)

	req, _ = http.NewRequest("PUT", "/api/characters/1", bytes.NewBuffer(goodJson))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")
	
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Ожидался статус 200, получили %d. Ответ: %s", w.Code, w.Body.String())
	}

	// Проверяем, что поля в базе обновились и AC пересчитался
	var updatedChar models.Character
	config.DB.First(&updatedChar, testChar.ID)

	if updatedChar.Name != "Алёшка" || updatedChar.Level != 3 {
		t.Errorf("Данные персонажа не обновились в БД")
	}

	if updatedChar.ArmorClass != 13 {
		t.Errorf("Класс доспеха (AC) рассчитан неверно: ожидали 13, получили %d", updatedChar.ArmorClass)
	}
}