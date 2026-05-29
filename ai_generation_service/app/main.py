# app/main.py
from fastapi import FastAPI, HTTPException, status
from .schemas import CharacterGenerationRequest
from .tasks import celery_app, generate_character_task 

app = FastAPI(title="From Zero To Frog - AI Character Service")

@app.post("/api/v1/generate", status_code=status.HTTP_202_ACCEPTED)
async def start_generation(payload: CharacterGenerationRequest):
    """
    Принимает концепт текста, запускает Celery задачу через .delay()
    """
    task = generate_character_task.delay(payload.concept) 
    
    return {
        "task_id": task.id,
        "status": "pending",
        "message": "Генерация персонажа успешно запущена."
    }

@app.get("/api/v1/status/{task_id}")
async def check_status(task_id: str):
    res = celery_app.AsyncResult(task_id)
    
    if res.state == "PENDING":
        return {"status": "pending"}
        
    elif res.state == "FAILURE":
        return {
            "status": "error",
            "error": str(res.result)
        }
        
    elif res.state == "SUCCESS":
        return {
            "status": "success",
            "character": res.result
        }