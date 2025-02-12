
import os
import pandas as pd
from fastapi import FastAPI, HTTPException, APIRouter
import dede_collection

app = FastAPI()
router = APIRouter()

# Percorso del file CSV della lista IBA
CSV_FILE_PATH = "data/cocktails.csv"

# Mappatura nome drink → immagine
image_name_mapping = {
    "CL": ("CL.jpg","Cuba Libre"),
    "FC": ("FC.jpg","French Connection"),
    "HN": ("HN.jpg","Horses Neck"),
    "V": ("V.jpg","Vesper"),
    "RSP": ("RSP.jpg","Russian Spring Punch"),
    "VE": ("VE.jpg","VE.N.TO"),
    "Black-Russian": ("BlackRussian.jpg", "Black Russian"),
    "Bloody-Mary": ("BloodyMary.jpg", "Bloody Mary"),
    "Champagne-Cocktail": ("ChampagneCocktail.jpg", "Champagne Cocktail"),
    "Corpse-Reviver-2": ("CorpseReviver2.jpg", "Corpse Reviver 2"),
    "French-75": ("French75.jpg", "French 75"),
    "Golden-Dream": ("GoldenDream.jpg", "Golden Dream"),
    "Hemingway-Special": ("HemingwaySpecial.jpg", "Hemingway Special"),
    "Irish-Coffee": ("IrishCoffee.jpg", "Irish Coffee"),
    "Long-Island-Ice-Tea": ("LongIslandIceTea.jpg", "Long Island Ice Tea"),
    "Mai-Tai": ("MaiTai.jpg", "Mai Tai"),
    "Mint-Julep": ("MintJulep.jpg", "Mint Julep"),
    "Moscow-Mule": ("MoscowMule.jpg", "Moscow Mule"),
    "Pina-Colada": ("PinaColada.jpg", "Pina Colada"),
    "Pisco-Sour": ("PiscoSour.jpg", "Pisco Sour"),
    "Sea-Breeze": ("SeaBreeze.jpg", "Sea Breeze"),
    "Sex-on-the-Beach": ("SexontheBeach.jpg", "Sex on the Beach"),
    "Singapore-Sling": ("SingaporeSling.jpg", "Singapore Sling"),
    "Tequila-Sunrise": ("TequilaSunrise.jpg", "Tequila Sunrise"),
    "Bees-Knees": ("BeesKnees.jpg", "Bees Knees"),
    "Dark-n-stormy": ("Darknstormy.jpg", "Dark 'n' Stormy"),
    "Espresso-Martini": ("EspressoMartini.jpg", "Espresso Martini"),
    "French-Martini": ("FrenchMartini.jpg", "French Martini"),
    "Lemon-drop-Martini": ("LemondropMartini.jpg", "Lemon Drop Martini"),
    "Naked-and-Famous": ("NakedandFamous.jpg", "Naked and Famous"),
    "New-York-Sour": ("NewYorkSour.jpg", "New York Sour"),
    "Old-Cuban": ("OldCuban.jpg", "Old Cuban"),
    "Paper-Plane": ("PaperPlane.jpg", "Paper Plane"),
    "Spicy-Fifty": ("SpicyFifty.jpg", "Spicy Fifty"),
    "Suffering-Bastard": ("SufferingBastard.jpeg", "Suffering Bastard"),
    "Tommys-Margarita": ("TommysMargarita.jpg", "Tommys Margarita"),
    "Trinidad-Sour": ("TrinidadSour.jpg", "Trinidad Sour"),
    "Yellow-Bird": ("YellowBird.jpg", "Yellow Bird"),
    "Angel-Face": ("AngelFace.jpg","Angel Face"),
    "Clover-Club": ("CloverClub.jpg", "Clover Club"),
    "Dry-Martini": ("DryMartini.jpg","Dry Martini"),
    "Gin-Fizz": ("GinFizz.jpg","Gin Fizz"),
    "Hanky-Panky": ("HankyPanky.jpg", "Hanky Panky"),
    "John-Collins": ("JohnCollins.jpg","John Collins"),
    "Last-Word": ("Lastword.jpg","Last Word"),
    "Mary-Pickford": ("MaryPickford.jpg","Mary Pickford"),
    "Monkey-Gland": ("MonkeyGland.jpg","Monkey Gland"),
    "Old-Fashioned": ("OldFashioned.jpg","Old Fashioned"),
    "Porto-Flip": ("PortoFlip.jpg","Porto Flip"),
    "Ramos-Fizz": ("RamosFizz.jpg","Ramos Fizz"),
    "Rusty-Nail": ("RustyNail.jpg","Rusty Nail"),
    "Vieux-Carr": ("VieuxCarr.jpg","Vieux Carr"),
    "Whiskey-Sour": ("WhiskeySour.jpg","Whiskey Sour"),
    "White-Lady": ("WhiteLady.jpg","White Lady"),
    "Between-the-Sheets": ("BetweentheSheets.jpg","Between-the-Sheets")

}

# Funzione per caricare il CSV
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8', sep=';')
        return df.dropna(subset=['NOME'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel caricamento del file CSV: {e}")

# Endpoint per ottenere la lista delle categorie
@router.get("/categories")
def get_categories():
    return ["Lista IBA", "Dede's Collection", "Altri"]

# Endpoint per ottenere la lista dei drink di una categoria
@router.get("/drinks/{category}")
def get_drinks_by_category(category: str):
    if category == "Lista IBA":
        df = load_csv(CSV_FILE_PATH)
        drink_names = [image_name_mapping.get(name, (None, name))[1] for name in df["NOME"].str.strip().unique()]
        return sorted(drink_names)
    elif category == "Dede's Collection":
        return dede_collection.get_dede_drinks()
    else:
        return []

# Endpoint per ottenere i dettagli di un drink
@router.get("/drink/{category}/{drink_name}")
def get_drink_details(category: str, drink_name: str):
    if category == "Lista IBA":
        df = load_csv(CSV_FILE_PATH)
        full_drink_name = next((key for key, val in image_name_mapping.items() if val[1] == drink_name), drink_name)
        drink_info = df[df["NOME"].str.strip().str.lower() == full_drink_name.lower()]
        if drink_info.empty:
            raise HTTPException(status_code=404, detail=f"Drink '{drink_name}' non trovato nella categoria '{category}'.")

        row = drink_info.iloc[0]
        return {
            "name": row['NOME'],
            "class": row.get('CLASSE', 'Dato non disponibile'),
            "gradazione": row.get('GRADAZIONE', 'Dato non disponibile'),
            "bicchiere": row.get('BICCHIERE', 'Dato non disponibile'),
            "ingredients": [{"name": row[f"INGREDIENTE.{i}"], "quantity": row[f"QUANTITA.{i}"]}
                             for i in range(9) if pd.notna(row.get(f"INGREDIENTE.{i}"))]
        }

    elif category == "Dede's Collection":
        return dede_collection.get_dede_drink_details(drink_name)
    else:
        raise HTTPException(status_code=400, detail=f"Categoria '{category}' non valida.")

app.include_router(router)
