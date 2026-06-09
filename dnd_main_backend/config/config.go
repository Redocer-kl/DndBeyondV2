package config

import "os"


var AIServiceURL string

func LoadConfig() {
    AIServiceURL = os.Getenv("AI_SERVICE_URL")
    if AIServiceURL == "" {
        AIServiceURL = "http://localhost:8081" 
    }
}