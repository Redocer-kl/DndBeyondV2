package handlers

import (
	"net/http"
	"dndbeyondv2/dndbackend/config"
	"dndbeyondv2/dndbackend/models"
	"dndbeyondv2/dndbackend/services"

	"github.com/gin-gonic/gin"
)

// UpdateCharacterInput - структура для валидации входящих данных на редактирование
type UpdateCharacterInput struct {
	Name         string `json:"name"`
	Level        int    `json:"level"`
	Strength     int    `json:"strength"`
	Dexterity    int    `json:"dexterity"`
	Constitution int    `json:"constitution"`
	Intelligence int    `json:"intelligence"`
	Wisdom       int    `json:"wisdom"`
	Charisma     int    `json:"charisma"`
}

// GetProfile - Получить данные вошедшего пользователя
func GetProfile(c *gin.Context) {
	userID, _ := c.Get("userID")

	var user models.User
	if err := config.DB.First(&user, userID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Пользователь не найден"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"user": user})
}

// GetUserCharacters - Получить персонажей привязанных к профилю (SELECT * WHERE user_id = ...)
func GetUserCharacters(c *gin.Context) {
	userID, _ := c.Get("userID")

	var characters []models.Character
	config.DB.Where("user_id = ?", userID).Find(&characters)

	c.JSON(http.StatusOK, gin.H{"characters": characters})
}

// UpdateCharacter - Изменение персонажа с валидацией (Аналог метода update() в сериализаторе)
func UpdateCharacter(c *gin.Context) {
	userID, _ := c.Get("userID")
	charID := c.Param("id") // Вытаскиваем /api/characters/:id из URL

	var character models.Character
	// Проверяем, существует ли персонаж И принадлежит ли он текущему юзеру
	if err := config.DB.Where("id = ? AND user_id = ?", charID, userID).First(&character).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Персонаж не найден или доступ запрещен"})
		return
	}

	var input UpdateCharacterInput
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// ---- Слой валидации (Бизнес-логика) ----
	if input.Level != 0 && (input.Level < 1 || input.Level > 20) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Уровень должен быть от 1 до 20"})
		return
	}

	stats := map[string]int{
		"strength":     input.Strength,
		"dexterity":    input.Dexterity,
		"constitution": input.Constitution,
		"intelligence": input.Intelligence,
		"wisdom":       input.Wisdom,
		"charisma":     input.Charisma,
	}

	for statName, val := range stats {
		// В Go дефолтное значение int = 0. Если оно 0, значит поле не прислали в JSON, пропускаем.
		if val != 0 && (val < 1 || val > 30) {
			c.JSON(http.StatusBadRequest, gin.H{"error": statName + " должна быть в диапазоне от 1 до 30"})
			return
		}
	}

	// Обновляем поля, если они были переданы
	if input.Name != "" { character.Name = input.Name }
	if input.Level != 0 { character.Level = input.Level }
	if input.Strength != 0 { character.Strength = input.Strength }
	if input.Dexterity != 0 { character.Dexterity = input.Dexterity }
	if input.Constitution != 0 { character.Constitution = input.Constitution }
	if input.Intelligence != 0 { character.Intelligence = input.Intelligence }
	if input.Wisdom != 0 { character.Wisdom = input.Wisdom }
	if input.Charisma != 0 { character.Charisma = input.Charisma }

	// Пересчитываем AC по Ловкости (базовый расчет)
	character.ArmorClass = 10 + ((character.Dexterity - 10) / 2)

	// Сохраняем изменения
	config.DB.Save(&character)

	c.JSON(http.StatusOK, gin.H{"status": "success", "character": character})
}

type GenerateInput struct {
	Concept string `json:"concept" binding:"required"`
}

func StartGeneration(c *gin.Context) {
	userID, _ := c.Get("userID")

	var input GenerateInput
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Поле concept обязательно"})
		return
	}

	// Создаем лог со статусом pending в нашей БД
	logEntry := models.AIConceptLog{
		UserID:  userID.(uint),
		Concept: input.Concept,
		Status:  "pending",
	}
	if err := config.DB.Create(&logEntry).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка базы данных"})
		return
	}

	// Отправляем задачу в RabbitMQ для Python-воркера
	err := services.PublishTask(logEntry.ID, logEntry.UserID, logEntry.Concept)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Не удалось отправить задачу в очередь: " + err.Error()})
		return
	}

	// Отдаем ответ фронтенду за несколько миллисекунд
	c.JSON(http.StatusAccepted, gin.H{
		"task_id": logEntry.ID,
		"status":  "pending",
		"message": "Генерация персонажа запущена через RabbitMQ",
	})
}