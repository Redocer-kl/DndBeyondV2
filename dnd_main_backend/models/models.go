package models

import (
	"time"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

// User - Модель пользователя
type User struct {
	ID        uint           `gorm:"primaryKey" json:"id"`
	Username  string         `gorm:"unique;not null" json:"username"`
	Email     string         `gorm:"unique;not null" json:"email"`
	Password  string         `gorm:"not null" json:"-"` // Пароль не отдаем в JSON
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

// Хеширование пароля перед сохранением 
func (u *User) HashPassword() error {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(u.Password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}
	u.Password = string(hashedPassword)
	return nil
}

// Проверка пароля при логине
func (u *User) CheckPassword(password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(u.Password), []byte(password))
	return err == nil
}

// Character - Модель персонажа 
type Character struct {
	ID           uint      `gorm:"primaryKey" json:"id"`
	UserID       uint      `gorm:"not null" json:"user_id"`
	Name         string    `gorm:"size:100;not null" json:"name"`
	Race         string    `gorm:"size:50" json:"race"`
	CharClass    string    `gorm:"size:50" json:"char_class"`
	Subclass     string    `gorm:"size:50" json:"subclass"`
	Level        int       `gorm:"default:1" json:"level"`
	
	// Характеристики
	Strength     int       `gorm:"default:8" json:"strength"`
	Dexterity    int       `gorm:"default:8" json:"dexterity"`
	Constitution int       `gorm:"default:8" json:"constitution"`
	Intelligence int       `gorm:"default:8" json:"intelligence"`
	Wisdom       int       `gorm:"default:8" json:"wisdom"`
	Charisma     int       `gorm:"default:8" json:"charisma"`

	ArmorClass   int       `gorm:"default:10" json:"armor_class"`
	Speed        int       `gorm:"default:30" json:"speed"`
	MaxHP        int       `gorm:"default:10" json:"max_hp"`
	CurrentHP    int       `gorm:"default:10" json:"current_hp"`
	HitDie       string    `gorm:"size:10;default:'1d8'" json:"hit_die"`
	Alignment    string    `gorm:"size:50" json:"alignment"`
	Background   string    `gorm:"size:100" json:"background"`
	Backstory    string    `gorm:"type:text" json:"backstory"`
	
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	IsDraft		 bool 	   `gorm:"bool" json:"is_draft"`
}

type AIConceptLog struct {
	ID           uint      `gorm:"primaryKey" json:"id"`
	UserID       uint      `json:"user_id"`
	Concept      string    `gorm:"type:text;not null" json:"concept"`
	Status       string    `gorm:"size:20;default:'pending'" json:"status"` // pending, success, error
	ErrorMessage string    `gorm:"type:text" json:"error_message"`
	CharacterID  *uint     `json:"character_id"` // Ссылка на созданного перса (может быть null)
	CreatedAt    time.Time `json:"created_at"`
}