import pandas as pd
import os
from fastapi import APIRouter, HTTPException

data_path = "data"

def load_csv(filename):
    try:
        return pd.read_csv(os.path.join(data_path, filename), encoding='utf-8', sep=';')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

dede_router = APIRouter()

dede_image_mapping = {
    "Lady's Negroni": ("LadysNegroni.jpg", "Lady's Negroni")
}

@dede_router.get("/dede/drinks")
def get_dede_drinks():
    df = load_csv("dede_collection.csv")
    return sorted([dede_image_mapping.get(name, (None, name))[1] for name in df['NOME'].str.strip().unique()])

@dede_router.get("/dede/drink/{drink_name}")
def get_dede_drink_details(drink_name: str):
    df = load_csv("dede_collection.csv")
    full_drink_name = next((key for key, value in dede_image_mapping.items() if value[1] == drink_name), drink_name)
    drink_data = df[df['NOME'].str.strip() == full_drink_name]
    if drink_data.empty:
        raise HTTPException(status_code=404, detail="Drink not found")
    return drink_data.to_dict(orient="records")[0]
