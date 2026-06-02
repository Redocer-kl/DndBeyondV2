package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

type PingResponse struct {
	Status  string `json:"status"`
	Message string `json:"message"`
}

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, "Привет! Основной бэкенд на Go работает.")
	})

	mux.HandleFunc("GET /api/ping", func(w http.ResponseWriter, r *http.Request) {
		response := PingResponse{
			Status:  "success",
			Message: "Понг!",
		}

		w.Header().Set("Content-Type", "application/json")
		
		json.NewEncoder(w).Encode(response)
	})

	port := ":8080"
	fmt.Printf("🚀 Сервер запущен на http://localhost%s\n", port)
	
	log.Fatal(http.ListenAndServe(port, mux))
}