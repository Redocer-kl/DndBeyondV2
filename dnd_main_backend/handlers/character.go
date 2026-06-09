package handlers

import (
	"net/http"
	"dndbeyondv2/dndbackend/config"
	"dndbeyondv2/dndbackend/models"
	"dndbeyondv2/dndbackend/services"
	"encoding/json"
	"fmt"
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
	// Достаем userID из контекста (после AuthMiddleware)
	userIDVal, exists := c.Get("userID")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Пользователь не авторизован"})
		return
	}
	userID := userIDVal.(uint)

	// Парсим концепт от фронтенда
	var req struct {
		Concept string `json:"concept"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Поле concept обязательно"})
		return
	}

	// 1. Создаем пустую запись лога со статусом pending
	logEntry := models.AIConceptLog{
		UserID:  userID,
		Concept: req.Concept,
		Status:  "pending",
	}
	if err := config.DB.Create(&logEntry).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Не удалось создать лог задачи"})
		return
	}

	// 2. Отправляем таску напрямую в RabbitMQ для Celery
	// Передаем logEntry.ID — в твоем сервисе он запишется в заголовок "id" сообщения,
	// благодаря чему ID задачи в Celery будет равен ID строки в нашей БД.
	if err := services.PublishTask(logEntry.ID, userID, req.Concept); err != nil {
		// Если RabbitMQ недоступен, сразу помечаем лог ошибкой, чтобы не зависал
		config.DB.Model(&logEntry).Updates(models.AIConceptLog{
			Status:       "error",
			ErrorMessage: "Ошибка отправки в брокер: " + err.Error(),
		})
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Брокер очередей недоступен"})
		return
	}

	// Отдаем фронту ID таски (он же ID лога) для последующего поллинга
	c.JSON(http.StatusAccepted, gin.H{
		"task_id": logEntry.ID,
		"status":  "pending",
		"message": "Задача успешно отправлена в очередь Celery",
	})
}

func GetGenerationStatus(c *gin.Context) {
	userIDVal, exists := c.Get("userID")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Пользователь не авторизован"})
		return
	}
	userID := userIDVal.(uint)

	logID := c.Param("id")

	var logEntry models.AIConceptLog
	if err := config.DB.Where("id = ? AND user_id = ?", logID, userID).First(&logEntry).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Задача не найдена"})
		return
	}

	if logEntry.Status == "success" {
		c.JSON(http.StatusOK, gin.H{"status": "success", "character_id": logEntry.CharacterID})
		return
	}
	if logEntry.Status == "error" {
		c.JSON(http.StatusBadRequest, gin.H{"status": "error", "error": logEntry.ErrorMessage})
		return
	}

	// ИСПОЛЬЗУЕМ ПЕРЕМЕННУЮ ИЗ КОНФИГА ВМЕСТО ХАРДКОДА
	// config.AIServiceURL теперь равен "http://localhost:8081" (из .env)
	fastApiURL := fmt.Sprintf("%s/api/v1/status/%d", config.AIServiceURL, logEntry.ID)
	
	resp, err := http.Get(fastApiURL)
	if err != nil {
		// Обязательно логируй ошибку в консоль бэкенда, чтобы видеть, если сеть отвалилась!
		fmt.Printf("[ОШИБКА] Запрос к FastAPI провалился: %v\n", err)
		c.JSON(http.StatusOK, gin.H{"status": "pending", "message": "ИИ-сервис временно недоступен..."})
		return
	}
	defer resp.Body.Close()

	var fastApiResp struct {
		Status    string                 `json:"status"`
		Error     string                 `json:"error"`
		Character map[string]interface{} `json:"character"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&fastApiResp); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка парсинга ответа от Celery"})
		return
	}

	switch fastApiResp.Status {
	case "pending":
		c.JSON(http.StatusOK, gin.H{"status": "pending", "message": "Оллама еще генерирует..."})
		return

	case "error":
		config.DB.Model(&logEntry).Updates(models.AIConceptLog{
			Status:       "error",
			ErrorMessage: fastApiResp.Error,
		})
		c.JSON(http.StatusBadRequest, gin.H{"status": "error", "error": fastApiResp.Error})
		return

	case "success":
		chData := fastApiResp.Character

		// Безопасные функции каста типов (числа из json парсятся в float64)
		getInt := func(key string) int {
			if val, ok := chData[key].(float64); ok {
				return int(val)
			}
			return 0
		}
		getString := func(key string) string {
			if val, ok := chData[key].(string); ok {
				return val
			}
			return ""
		}

		// Собираем модель. Поле modifiers просто игнорируем, в модели Character его нет.
		newChar := models.Character{
			UserID:       logEntry.UserID,
			Name:         getString("name"),
			Race:         getString("race"),
			CharClass:    getString("char_class"),
			Subclass:     getString("subclass"),
			Level:        getInt("level"),
			Strength:     getInt("strength"),
			Dexterity:    getInt("dexterity"),
			Constitution: getInt("constitution"),
			Intelligence: getInt("intelligence"),
			Wisdom:       getInt("wisdom"),
			Charisma:     getInt("charisma"),
			ArmorClass:   getInt("armor_class"),
			Speed:        getInt("speed"),
			MaxHP:        getInt("max_hp"),
			CurrentHP:    getInt("current_hp"),
			HitDie:       getString("hit_die"),
			Alignment:    getString("alignment"),
			Background:   getString("background"),
			Backstory:    getString("backstory"),
			IsDraft:      true,
		}

		tx := config.DB.Begin()
		if err := tx.Create(&newChar).Error; err != nil {
			tx.Rollback()
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка сохранения персонажа в БД"})
			return
		}

		logEntry.Status = "success"
		logEntry.CharacterID = &newChar.ID
		if err := tx.Save(&logEntry).Error; err != nil {
			tx.Rollback()
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка обновления лога"})
			return
		}
		tx.Commit()

		c.JSON(http.StatusOK, gin.H{
			"status":       "success",
			"character_id": newChar.ID,
		})
		return

	default:
		c.JSON(http.StatusOK, gin.H{"status": "pending"})
		return
	}
}


func GetCharacter(c *gin.Context) {
	userID, _ := c.Get("userID")
	charID := c.Param("id")

	var character models.Character

	// Запрашиваем персонажа, проверяя, что он принадлежит именно этому пользователю
	if err := config.DB.Where("id = ? AND user_id = ?", charID, userID).First(&character).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Персонаж не найден или у вас нет к нему доступа"})
		return
	}

	// Отдаем всю структуру со статами, расой, классом и историей
	c.JSON(http.StatusOK, character)
}