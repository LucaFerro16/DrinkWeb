
import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()

data_path = "data/cocktails.csv"

def load_csv(file_path):
    try:
        return pd.read_csv(file_path, encoding='ISO-8859-1', sep=';')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {file_path} non esiste.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search_drink/{drink_name}")
def search_drink(drink_name: str):
    df = load_csv(data_path)

    # Verifica se il nome del drink è nella colonna 'NOME'
    drink_info = df[df['NOME'].str.contains(drink_name, case=False, na=False)]

    # Se il drink esiste, prepariamo i dettagli da restituire
    if not drink_info.empty:
        results = []
        for _, row in drink_info.iterrows():
            drink_details = {
                "name": row['NOME'],
                "class": row['CLASSE'],
                "gradazione": row['GRADAZIONE'],
                "bicchiere": row['BICCHIERE'],
                "ingredients": []
            }

            # Ingredienti e quantità
            ingredients = [col for col in df.columns if "INGREDIENTE" in col]
            quantities = [col for col in df.columns if "QUANTITA" in col]

            for i, ingredient in enumerate(ingredients):
                if pd.notna(row[ingredient]):
                    drink_details["ingredients"].append({
                        "ingredient": row[ingredient],
                        "quantity_ml": row[quantities[i]]
                    })

            results.append(drink_details)

        return results
    else:
        raise HTTPException(status_code=404, detail=f"Il drink '{drink_name}' non è stato trovato.")
