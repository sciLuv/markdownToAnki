import re
import os
import shutil
import csv
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(dotenv_path)


if os.path.exists(dotenv_path):
    print(f"Chargement du fichier .env depuis : {dotenv_path}")
    load_dotenv(dotenv_path)
else:
    print(f"Le fichier .env n'existe pas à l'emplacement : {dotenv_path}")

def reformat_markdown(markdown_file, output_file, audio_base_path, media_dir):
    with open(markdown_file, 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    # Remove tabs and spaces at the beginning and end of lines
    content = re.sub(r'\t+', ' ', content)
    content = re.sub(r' +', ' ', content)
    content = content.strip()

    # Remove double newlines
    content = re.sub(r'\n\s*\n', '\n', content)

    formatted_lines = []

    current_category = ""

    lines = content.splitlines()

    for line in lines:
        # Ignore lines containing "texte en chinois" (case-insensitive)
        if re.search(r'texte en chinois', line, re.IGNORECASE):
            continue

        # Detect category titles
        category_match = re.match(r'^\s*#{1,6}\s*(.+?)\s*$', line)
        if category_match:
            current_category = category_match.group(1).strip()
            formatted_lines.append(f"*{current_category}*")
            continue

        # Process table lines
        if line.startswith("|") and not re.match(r'\|[-\s]+\|', line):
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if len(cells) >= 4:
                chinese_word = cells[0]
                pinyin = cells[1]
                translation = cells[2]
                word_type = cells[3]

                # Handle audios if present
                audio_references = cells[4] if len(cells) > 4 else ''
                audio_files = []

                if audio_references:
                    audio_matches = re.findall(r'\[\[(.+?)\]\]', audio_references)
                    for audio_reference in audio_matches:
                        audio_path = os.path.join(audio_base_path, audio_reference)
                        if os.path.exists(audio_path):
                            # Copy the audio file to Anki's collection.media folder
                            media_name = copy_media_to_anki(audio_path, media_dir)
                            if media_name:
                                audio_files.append(f"[sound:{media_name}]")
                        else:
                            print(f"Audio file not found: {audio_path}")

                # Add sounds to the translation field
                if audio_files:
                    translation += ' ' + ' '.join(audio_files)

                # Build the formatted line
                formatted_line = f"{chinese_word}|{word_type}|{pinyin}|{translation}"
                formatted_lines.append(formatted_line)

    # Write all formatted lines to the output file
    with open(output_file, 'w', encoding='utf-8', newline='') as out_file:
        writer = csv.writer(out_file, delimiter='|')
        writer.writerows([line.split('|') for line in formatted_lines])

def copy_media_to_anki(media_file, media_dir):
    """
    Copies the media file to Anki's collection.media folder and returns the file name.
    """
    media_name = os.path.basename(media_file)
    dest_file = os.path.join(media_dir, media_name)
    
    if not os.path.exists(dest_file):
        try:
            shutil.copy(media_file, dest_file)
            print(f"Copied: {media_name} to {dest_file}")
        except Exception as e:
            print(f"Failed to copy {media_name}: {e}")
            return None
    else:
        print(f"Media file already exists: {media_name}")
    
    return media_name

def process_markdown_files(root_dir, audio_base_path, output_dir, media_dir):
    """
    Clears the output directory before starting, then recursively processes the folder.
    """
    clear_output_directory(output_dir)

    # Recursively walk through the directory
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                markdown_file = os.path.join(subdir, file)
                output_file = os.path.join(output_dir, os.path.splitext(file)[0] + '.csv')
                reformat_markdown(markdown_file, output_file, audio_base_path, media_dir)
                print(f"Processed {markdown_file} -> {output_file}")

def clear_output_directory(output_dir):
    """
    Deletes all content in the output directory.
    """
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)



# Example usage
root_dir = os.getenv('ROOT_DIR')
audio_directory = os.getenv('AUDIO_DIRECTORY')
media_dir = os.getenv('MEDIA_DIR')
output_dir = "./output_csv"

# Step 1: Reformat Markdown files into CSV
process_markdown_files(root_dir, audio_directory, output_dir, media_dir)
