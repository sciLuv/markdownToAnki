import csv
import os
import json
import requests
import re
import logging
import unicodedata
from concurrent.futures import ThreadPoolExecutor

# Charger le fichier styles.json
def load_styles(style_file):
    if os.path.exists(style_file):
        with open(style_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}  # Retourner un dictionnaire vide si le fichier n'existe pas

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Fonction pour charger les styles depuis un fichier JSON
def load_styles(style_file):
    if os.path.exists(style_file):
        with open(style_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def create_deck(deck_name):
    request = {
        "action": "createDeck",
        "version": 6,
        "params": {
            "deck": deck_name
        }
    }
    try:
        response = requests.post('http://localhost:8765', json=request).json()
        if response.get("error"):
            logging.error(f"Error creating deck '{deck_name}': {response['error']}")
        else:
            logging.info(f"Deck '{deck_name}' created or already exists.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error to AnkiConnect when creating deck '{deck_name}': {e}")

def find_note_id(front_html):
    # On garde la recherche avec le texte brut ici
    note_type = "Basique"
    field_name = "Recto"
    
    # Nettoyage et normalisation du texte HTML pour la recherche
    normalized_html = unicodedata.normalize('NFC', front_html.strip())
    escaped_html = normalized_html.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
    
    query = f'note:"{note_type}" {field_name}:"{escaped_html}"'
    logging.info(f"Querying Anki for: {query}")

    request = {
        "action": "findNotes",
        "version": 6,
        "params": {
            "query": query
        }
    }

    try:
        # Envoi de la requête à AnkiConnect
        response = requests.post('http://localhost:8765', json=request).json()
        logging.info(f"Response from Anki: {response}")
        
        if response.get("error"):
            logging.error(f"Error finding notes: {response['error']}")
            return []
        
        note_ids = response.get('result', [])
        if not note_ids:
            logging.info(f"No existing note found for front '{front_html}'.")
            return []
        
        logging.info(f"Found note IDs for front '{front_html}': {note_ids}")
        return note_ids

    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error to AnkiConnect: {e}")
        return []

def update_note_in_anki(note_id, front_html, back_html, tags):
    note = {
        "note": {
            "id": note_id,
            "fields": {
                "Recto": front_html,
                "Verso": back_html
            },
            "tags": tags
        }
    }
    request = {
        "action": "updateNoteFields",
        "version": 6,
        "params": note
    }
    
    try:
        response = requests.post('http://localhost:8765', json=request).json()
        logging.info(f"Response from Anki (update): {response}")
        
        if response.get("error"):
            logging.error(f"Error updating note {note_id}: {response['error']}")
        else:
            logging.info(f"Successfully updated note with ID: {note_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error to AnkiConnect when updating note {note_id}: {e}")

def add_note_to_anki(deck_name, model_name, front_html, back_html, tags):
    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": {
            "Recto": front_html,
            "Verso": back_html
        },
        "tags": tags,
        "options": {
            "allowDuplicate": False,
            "duplicateScope": "collection",
            "duplicateScopeFields": ["Recto"]
        }
    }
    
    request = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": note
        }
    }

    try:
        response = requests.post('http://localhost:8765', json=request).json()
        logging.info(f"Response from Anki (add): {response}")
        
        if response.get("error"):
            if "duplicate" in response['error'].lower():
                logging.info(f"Note with front '{front_html}' is a duplicate, attempting to update.")
            else:
                logging.error(f"Error adding note: {response['error']}")
        else:
            logging.info(f"Successfully added note with front '{front_html}'.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error to AnkiConnect when adding note: {e}")

    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": {
            "Recto": front_html,
            "Verso": back_html
        },
        
        "tags": tags,
        "options": {
            "allowDuplicate": False,
            "duplicateScope": "collection",
            "duplicateScopeFields": ["Recto"]
        }
    }
    try:
        request = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": note
            }
        }

        response = requests.post('http://localhost:8765', json=request).json()
        if response.get("error"):
            if "duplicate" in response['error'].lower():
                logging.info(f"Note with front '{front_html}' is a duplicate, attempting to update.")
            else:
                logging.error(f"Error adding note: {response['error']}")
        else:
            logging.info(f"Added note with front '{front_html}'.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error to AnkiConnect when adding note: {e}")

def add_or_update_note_in_anki(deck_name, model_name, front_text, front_html, back_html, tags):
    logging.info(f"Processing note with front_html: {front_html}")
    
    # Recherche de la note existante
    note_ids = find_note_id(front_html)
    
    # Si la note existe déjà, on la met à jour
    if note_ids:
        logging.info(f"Updating existing note IDs: {note_ids}")
        for note_id in note_ids:
            update_note_in_anki(note_id, front_html, back_html, tags)
    else:
        # Si elle n'existe pas, on l'ajoute
        logging.info(f"Adding new note with front_html: {front_html}")
        add_note_to_anki(deck_name, model_name, front_html, back_html, tags)

def format_back_html(pinyin, translation, audio_list=None, styles=None):
    audio_html = ""
    if audio_list:
        for audio in audio_list:
            audio_html += f'<div style="margin-top: 15px;"><audio controls src="{audio}"></audio></div>'
    
    # Styles par défaut
    default_pinyin_style = "font-size: 28px; color: #FF5733; font-weight: bold; margin-bottom: 15px;"
    default_translation_style = "font-size: 22px; color: white; margin-bottom: 15px;"
    
    # Charger les styles spécifiques si définis dans styles.json
    pinyin_style = styles.get('pinyin_style', default_pinyin_style) if styles else default_pinyin_style
    translation_style = styles.get('translation_style', default_translation_style) if styles else default_translation_style
    
    # Construire le HTML pour le verso (back)
    back_html = f"""
    <div style="{pinyin_style}">{pinyin}</div>
    <div style="{translation_style}">{translation}</div>
    {audio_html}
    """
    return back_html

def format_front_html(front, styles=None):
    # Style par défaut
    default_style = "font-size: 36px; color: #2E86C1; font-weight: bold; text-align: center; margin-top: 50px;"
    
    # Charger le style spécifique si défini dans styles.json
    front_style = styles.get('front_style', default_style) if styles else default_style
    
    # Retourner le HTML formaté pour le front (recto)
    return f'<div style="{front_style}">{front}</div>'

def process_csv_file_for_anki(csv_file, global_deck_name, model_name):
    styles = load_styles(styles_json_path)
    csv_deck_name = os.path.splitext(os.path.basename(csv_file))[0].strip()
    deck_name = f"{global_deck_name}::{csv_deck_name}"
    
    # Create global and specific decks
    create_deck(global_deck_name)
    create_deck(deck_name)
    current_category = None

    notes = []

    # Read CSV file and prepare note data
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='|')

        for row in reader:
            if not row:
                continue  # Skip empty lines
            if len(row) == 1 and row[0].startswith("*") and row[0].endswith("*"):
                current_category = row[0].strip("*").strip()
                logging.info(f"New category detected: {current_category}")
                continue  # Move to next line

            if len(row) >= 4:
                front = row[0].strip()
                word_type = row[1].strip()
                pinyin = row[2].strip()
                translation = row[3].strip()

                # Build deck name
                if current_category:
                    note_deck_name = f"{deck_name}::{current_category}"
                    create_deck(note_deck_name)
                else:
                    note_deck_name = deck_name

                front_text = front.strip()
                front_html = format_front_html(front, styles)

                # Extract all sounds from translation field
                audio_list = re.findall(r'\[sound:(.*?)\]', translation)
                # Remove [sound:...] tags from translation
                translation_clean = re.sub(r'\[sound:.*?\]', '', translation).strip()

                back_html = format_back_html(pinyin, translation_clean, audio_list, styles)

                notes.append((note_deck_name, model_name, front_text, front_html, back_html, [word_type]))
            else:
                logging.warning(f"Ignored line in file {csv_file}: {row}")

    logging.info(f"Processing CSV file: {csv_file} with {len(notes)} notes.")

    if not notes:
        logging.warning(f"No notes to process in file {csv_file}.")
        return

    with ThreadPoolExecutor() as executor:
        for note in notes:
            executor.submit(add_or_update_note_in_anki, *note)

def process_all_csv_files_for_anki(directory, global_deck_name, model_name="Basique"):
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]
    logging.info(f"Found CSV files: {csv_files}")
    for file in csv_files:
        csv_file = os.path.join(directory, file)
        process_csv_file_for_anki(csv_file, global_deck_name, model_name)


styles_json_path = os.path.join(os.path.dirname(__file__), 'config', 'styles.json')


if __name__ == "__main__":
    output_dir = "./output_csv"
    global_deck_name = "Global"
    process_all_csv_files_for_anki(output_dir, global_deck_name)
