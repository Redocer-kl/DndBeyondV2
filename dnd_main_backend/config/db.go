package config

import (
	"fmt"
	"log"
	"os"
	"dndbeyondv2/dndbackend/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func ConnectDatabase() {
	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=%s",
		os.Getenv("DB_HOST"),
		os.Getenv("DB_USER"),
		os.Getenv("DB_PASSWORD"),
		os.Getenv("DB_NAME"),
		os.Getenv("DB_PORT"),
		os.Getenv("DB_SSLMODE"),
	)

	database, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("Не удалось подключиться к базе данных: ", err)
	}

	// Автомиграция (создание/обновление таблиц)
	err = database.AutoMigrate(&models.User{}, &models.Character{})
	if err != nil {
		log.Fatal("Ошибка миграции: ", err)
	}

	DB = database
	fmt.Println("💾 База данных успешно подключена и мигрирована!")
}