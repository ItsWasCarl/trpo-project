import json
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/products", tags=["medications"])

DATA_FILE = os.path.join(os.path.dirname(__file__), "medications.json")


def load_medications():
    if not os.path.exists(DATA_FILE):
        initial_data = [
            {"id": 1, "name": "Парацетамол", "manufacturer": "Фармстандарт", "price": 50,
             "expiration_date": "2025-12-31", "availability": True},
            {"id": 2, "name": "Ибупрофен", "manufacturer": "Хемофарм", "price": 80, "expiration_date": "2024-06-30",
             "availability": True},
            {"id": 3, "name": "Амоксициллин", "manufacturer": "Синтез", "price": 120, "expiration_date": "2025-03-01",
             "availability": False}
        ]
        save_medications(initial_data)
        return initial_data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_medications(medications):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(medications, f, ensure_ascii=False, indent=4)


@router.get("/")
async def get_medications(
        sorting: Optional[str] = Query(None, pattern="^(asc|desc)$",
                                       description="Сортировка по названию: asc или desc"),
        manufacturer: Optional[str] = Query(None,
                                            description="Фильтр по производителю (точное совпадение, без учёта регистра)")
):
    meds = load_medications()

    if manufacturer:
        meds = [m for m in meds if m["manufacturer"].lower() == manufacturer.lower()]

    if sorting:
        reverse = sorting == "desc"
        meds.sort(key=lambda x: x["name"], reverse=reverse)

    return {"medications": meds, "total": len(meds)}


@router.get("/{id}")
async def get_medication(id: int):
    meds = load_medications()
    for med in meds:
        if med["id"] == id:
            return med
    raise HTTPException(status_code=404, detail="Лекарство не найдено")


@router.post("/", status_code=201)
async def create_medication(medication: dict):
    required = ["name", "manufacturer", "price", "expiration_date", "availability"]
    for field in required:
        if field not in medication:
            raise HTTPException(status_code=400, detail=f"Отсутствует поле: {field}")

    meds = load_medications()
    new_id = max((m["id"] for m in meds), default=0) + 1
    medication["id"] = new_id
    meds.append(medication)
    save_medications(meds)
    return medication


@router.put("/{id}")
async def update_medication(id: int, updated: dict):
    required = ["name", "manufacturer", "price", "expiration_date", "availability"]
    for field in required:
        if field not in updated:
            raise HTTPException(status_code=400, detail=f"Отсутствует поле: {field}")

    meds = load_medications()
    for i, med in enumerate(meds):
        if med["id"] == id:
            updated["id"] = id
            meds[i] = updated
            save_medications(meds)
            return updated
    raise HTTPException(status_code=404, detail="Лекарство не найдено")


@router.delete("/{id}")
async def delete_medication(id: int):
    meds = load_medications()
    for i, med in enumerate(meds):
        if med["id"] == id:
            del meds[i]
            save_medications(meds)
            return {"message": "Лекарство удалено"}
    raise HTTPException(status_code=404, detail="Лекарство не найдено")