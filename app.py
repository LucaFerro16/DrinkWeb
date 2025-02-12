from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import pandas as pd
from urllib.parse import unquote
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Usa la porta di Render se disponibile
    uvicorn.run(app, host="0.0.0.0", port=port)


# Creazione app e configurazione di base
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Percorsi dei file dati
DATA_DIR = "data"
COCKTAILS_CSV = f"{DATA_DIR}/cocktails.csv"
DEDE_COLLECTION_CSV = f"{DATA_DIR}/dede_collection.csv"

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

# Funzione per caricare un CSV
def load_csv(file_path):
    try:
        return pd.read_csv(file_path, sep=";", encoding="utf-8").dropna(subset=['NOME'])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading CSV: {e}")


# Funzione per ottenere i drink in base alla categoria
def get_drinks_by_category(category):
    if category == "Lista IBA":
        df = load_csv(COCKTAILS_CSV)
    elif category == "Dede's Collection":
        df = load_csv(DEDE_COLLECTION_CSV)
    else:
        return []

    return sorted([image_name_mapping.get(name, (None, name))[1] for name in df["NOME"].str.strip().unique()])



# Funzione per ottenere i dettagli di un drink
@app.get("/drink-details", response_class=HTMLResponse)
def drink_details(request: Request, drink: str):
    drink = unquote(drink).replace("+", " ").strip()  # Decodifica e pulisce il nome

    # 🔹 Trova il nome corretto per la ricerca
    full_drink_name = next((key for key, val in image_name_mapping.items() if val[1] == drink), drink)

    # 🔹 Determina la categoria e carica i dati dal CSV corretto
    drink_info = None
    for file in ["data/cocktails.csv", "data/dede_collection.csv"]:
        df = load_csv(file)

        # 🔹 Cerca il drink nel CSV
        matches = df[df["NOME"].str.strip().str.lower() == full_drink_name.lower()]
        if not matches.empty:
            drink_info = matches.iloc[0].to_dict()
            break  # Se lo troviamo, ci fermiamo

    # 🔹 Se il drink non è stato trovato, restituiamo errore 404
    if not drink_info:
        raise HTTPException(status_code=404, detail="Drink non trovato")

    # 🔹 Costruisce il dizionario con i dettagli del drink
    formatted_drink_info = {
        "NOME": drink_info["NOME"],
        "GRADAZIONE": drink_info.get("GRADAZIONE", "Dato non disponibile"),
        "BICCHIERE": drink_info.get("BICCHIERE", "Dato non disponibile"),
        "INGREDIENTI": []
    }

    # 🔹 Estrai fino a 10 ingredienti con quantità
    for i in range(10):
        ingrediente_col = f"INGREDIENTE{'' if i == 0 else f'.{i}'}"
        quantita_col = f"QUANTITA{'' if i == 0 else f'.{i}'}"

        ingrediente = str(drink_info.get(ingrediente_col, "")).strip()
        quantità = str(drink_info.get(quantita_col, "")).strip()

        if ingrediente and ingrediente.lower() != "nan":
            formatted_drink_info["INGREDIENTI"].append(f"{ingrediente} ({quantità})")


    # Normalizziamo il nome dell'immagine rimuovendo caratteri speciali
    nome_pulito = formatted_drink_info['NOME']
    nome_pulito = nome_pulito.replace(" ", "-").replace("'", "").replace(".", "")

    # Percorso dell'immagine nella cartella static
    image_path = f"static/images/{nome_pulito}.jpg"

    # Se il drink è in image_name_mapping, usa il nome corretto per l'immagine
    if full_drink_name in image_name_mapping:
        image_path = f"static/images/{image_name_mapping[full_drink_name][0]}"

    # Controlliamo se l'immagine esiste davvero
    if not os.path.exists(image_path):
        print(f"⚠️ ATTENZIONE: L'immagine {image_path} NON ESISTE! Controlla il nome del file.")
        image_path = "/static/images/default.jpg"  # Fallback se l'immagine non esiste

    # Aggiungiamo la barra iniziale per renderlo compatibile con il server
    image_filename = f"/{image_path}"

    print(f"Caricamento immagine: {image_filename}")

    return templates.TemplateResponse("drink.html", {
        "request": request,
        "drink_name": image_name_mapping[full_drink_name][1] if full_drink_name in image_name_mapping else formatted_drink_info["NOME"],
        "drink_info": formatted_drink_info,
        "image_filename": image_filename,
        "ingredienti": formatted_drink_info["INGREDIENTI"]
    })




# Route per la pagina iniziale
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/select")
async def select_collection(collection: str = Form(...)):
    if collection == "Dede's Collection":
        return RedirectResponse(url="/select/dede", status_code=303)
    else:
        return RedirectResponse(url="/select/iba", status_code=303)
    
def select_drinks(request: Request, collection: str):
    file_path = "data/dede_collection.csv" if collection == "dede" else "data/cocktails.csv"
    drinks_df = load_csv(file_path)
    drinks = drinks_df["NOME"].tolist() if "NOME" in drinks_df.columns else []
    
    return templates.TemplateResponse("select.html", {
        "request": request,
        "drinks": drinks
    })
    
def drink_details(request: Request, drink: str):
    # Prima controlliamo se il drink è in image_name_mapping
    if drink in image_name_mapping:
        drink_info = {"NOME": image_name_mapping[drink][1], "IMMAGINE": image_name_mapping[drink][0], "INGREDIENTI": []}
    else:
        # Se non è in image_name_mapping, cerchiamo nei CSV
        drink_info = None
        for file in ["data/cocktails.csv", "data/dede_collection.csv"]:
            df = load_csv(file)
            if drink in df["NOME"].values:
                drink_info = df[df["NOME"] == drink].iloc[0].to_dict()
                break

        if not drink_info:
            raise HTTPException(status_code=404, detail="Drink non trovato")

    return templates.TemplateResponse("drink.html", {
        "request": request,
        "drink_name": drink_info["NOME"],
        "drink_info": drink_info,
        "image_filename": drink_info["IMMAGINE"],
        "ingredienti": drink_info.get("INGREDIENTI", "").split(", ")  # Split per lista di ingredienti
    })
    
def get_all_drinks(category: str = "Lista IBA"):
    # Determina quale file CSV utilizzare in base alla categoria
    if category == "Lista IBA":
        df = load_csv(COCKTAILS_CSV)
    elif category == "Dede's Collection":
        df = load_csv(DEDE_COLLECTION_CSV)
    else:
        raise HTTPException(status_code=400, detail="Categoria non valida")

    # Crea una lista di drink usando `image_name_mapping` se disponibile
    all_drinks = [
        (name, image_name_mapping[name][1]) if name in image_name_mapping else (name, name)
        for name in df["NOME"].str.strip().unique()
    ]
    print("DEBUG - PRIMI 10 DRINKS:", all_drinks[:70])
    return {"drinks": sorted(all_drinks, key=lambda x: x[1].lower())}



@app.get("/dede/drinks")
def get_dede_drinks():
    try:
        # Carica il file CSV con Pandas
        df = pd.read_csv("data/dede_collection.csv", encoding="utf-8", sep=";")
        # Restituisci una lista di drink (ad esempio la colonna 'NOME')
        return df["NOME"].dropna().tolist()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/select/{collection}", response_class=HTMLResponse)
async def select_drinks(request: Request, collection: str):
    if collection not in ["dede", "iba"]:
        raise HTTPException(status_code=404, detail="Collezione non trovata")

    file_path = "data/dede_collection.csv" if collection == "dede" else "data/cocktails.csv"
    drinks_df = load_csv(file_path)
    drinks = drinks_df["NOME"].tolist() if "NOME" in drinks_df.columns else []

    # Sostituiamo i nomi abbreviati con quelli completi se esistono in image_name_mapping
    drinks_display = [(drink, image_name_mapping[drink][1]) if drink in image_name_mapping else (drink, drink) for drink in drinks]

    return templates.TemplateResponse("select.html", {
        "request": request,
        "drinks": drinks_display
    })

