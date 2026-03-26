import logging
import uvicorn
from fastapi import FastAPI
from src.controllers.products import router as products_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Аптека API",
    description="API для управления списком лекарств",
    version="1.0.0",
)

app.include_router(products_router)

@app.get("/")
async def root():
    return {"message": "Это API для аптеки"}

def main():
    logger.info('Запуск приложения')
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

if __name__ == "__main__":
    main()