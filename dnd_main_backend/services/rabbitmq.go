package services

import (
	"context"
	"encoding/json"
	"time"
	"fmt"

	amqp "github.com/rabbitmq/amqp091-go"
)

// Структура сообщения, которую ожидает Celery-таска в Python
type CeleryMessage struct {
	Args []interface{} `json:"args"` // Массив позиционных аргументов для функции
}

// PublishTask - отправка задачи генерации в RabbitMQ
func PublishTask(logID uint, userID uint, concept string) error {
	// 1. Подключаемся к RabbitMQ
	conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
	if err != nil {
		return err
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		return err
	}
	defer ch.Close()

	// 2. Объявляем очередь (если её нет, RabbitMQ её создаст)
	// Имя очереди 'celery' — дефолтное для Celery
	q, err := ch.QueueDeclare(
		"celery", // name
		true,     // durable (выдержит ли очередь перезагрузку брокера)
		false,    // delete when unused
		false,    // exclusive
		false,    // no-wait
		nil,      // arguments
	)
	if err != nil {
		return err
	}

	// 3. Формируем тело сообщения для Celery таски: generate_character_task(log_id, user_id, user_concept)
	// Порядок в массиве Args должен строго совпадать с аргументами в Python!
	payload := CeleryMessage{
		Args: []interface{}{logID, userID, concept},
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// 4. Публикуем сообщение в очередь
	err = ch.PublishWithContext(ctx,
		"",     // exchange
		q.Name, // routing key (имя очереди)
		false,  // mandatory
		false,  // immediate
		amqp.Publishing{
			ContentType: "application/json",
			Body:        body,
			Headers: amqp.Table{
				// Важно для Celery: указываем имя таски, как она зарегистрирована в Python
				"id":   fmt.Sprintf("%d", logID), 
				"task": "tasks.generate_character_task", 
			},
		},
	)
	return err
}