import pandas as pd
import os
from fastapi import APIRouter, HTTPException

data_path = "data"

def load_csv(filename):
    try:
        return pd.read_csv(os.path.join(data_path, filename), encoding='ISO-8859-1', sep=';')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

drink_router = APIRouter()

@drink_router.get("/drinks")
def get_drinks():
    df = load_csv("cocktails.csv")
    return sorted(df['NOME'].dropna().str.strip().unique().tolist())

@drink_router.get("/drink/{drink_name}")
def get_drink_details(drink_name: str):
    df = load_csv("cocktails.csv")
    clean_drink_name = drink_name.replace('-', ' ').strip().lower()
    drink_data = df[df['NOME'].str.strip().str.lower() == clean_drink_name]
    if drink_data.empty:
        raise HTTPException(status_code=404, detail="Drink not found")
    return drink_data.to_dict(orient="records")[0]
