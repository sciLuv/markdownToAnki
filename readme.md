Conversion de fichiers Markdown en cartes Anki pour l'apprentissage du chinois

## Contexte

J'apprend le chinois depuis quelques mois et je cherchais un moyen efficace de mémoriser du vocabulaire. Une dame dans le métro m'a parler d'anki, une application open source spécialement faite pour l'apprentissage des langues et la mémorisation de ces dernieres.
J'avais de nombreuses notes stockées en markdown dans **Obsidian**, j'ai donc voulu automatiser la conversion de ces informations en cartes de révision anki. 

Ce script a donc été conçu pour les apprenants du chinois (donc je fais partie) et particulièrement ceux qui utilisent des fichiers Markdown pour organiser leur vocabulaire, et qui cherchent à les exploiter dans Anki pour améliorer leur apprentissage.

Le script lit les fichiers Markdown, extrait les mots chinois, pinyin, traductions et fichiers audio associés, puis les importe automatiquement dans Anki sous forme de cartes organisées en decks. Il est idéal pour ceux qui souhaitent tirer le meilleur parti de leurs notes tout en optimisant leur mémorisation grâce à Anki.

---

## Structure des fichiers Markdown pris en charge

Ce script est conçu pour traiter des notes structurées en tableaux Markdown, typiquement utilisées dans des applications comme **Obsidian**. Les informations sont organisées dans un tableau avec des colonnes pour le mot chinois, le pinyin, la traduction, le type de mot et, si nécessaire, un fichier audio.

### Exemple de tableau Markdown

```markdown
| Mot chinois | Pinyin  | Traduction | Type de mot  | Audio (optionnel)      |
|-------------|---------|------------|--------------|------------------------|
| 你好        | nǐ hǎo  | Bonjour    | Expression   | [[hello.mp3]]           |
| 谢谢        | xièxiè  | Merci      | Expression   | [[thanks.mp3]]          |
```

#### Colonnes prises en charge :
- **Mot chinois** : Le mot ou l'expression en chinois.
- **Pinyin** : La transcription phonétique du mot.
- **Traduction** : La traduction en français.
- **Type de mot** : Par exemple, "Nom", "Verbe", ou "Expression".
- **Audio (optionnel)** : Fichier audio pour la prononciation, référencé sous la forme `[[nom_du_fichier.mp3]]`.

### Catégories et titres de section (facultatif)

Si vos notes Markdown contiennent des titres de section, comme des catégories de vocabulaire, le script les utilisera pour organiser les cartes dans des sous-decks dans Anki.

Un titre de section est reconnu lorsqu'il est précédé de symboles `#` (par exemple, `### Salutations`). Le script détectera ces titres et créera des sous-decks en fonction de ces catégories.

#### Exemple avec catégories :

```markdown
### Salutations

| Mot chinois | Pinyin  | Traduction | Type de mot  | Audio (optionnel) |
|-------------|---------|------------|--------------|-------------------|
| 你好        | nǐ hǎo  | Bonjour    | Expression   | [[hello.mp3]]      |

### Expressions courantes

| Mot chinois | Pinyin  | Traduction | Type de mot  | Audio (optionnel) |
|-------------|---------|------------|--------------|-------------------|
| 谢谢        | xièxiè  | Merci      | Expression   | [[thanks.mp3]]     |
```

Dans cet exemple, le script générera deux sous-decks dans Anki :
- `vocabulaire::Salutations`
- `vocabulaire::Expressions courantes`

Chaque fichier Markdown dans le dossier source représentera donc une sous-partie du deck principal dans Anki, et les titres de section deviendront des sous-decks. Cela permet de maintenir une organisation claire dans Anki, surtout si vous gérez beaucoup de vocabulaire.

---

## Préparation et configuration

### Installation des modules requis

Avant d'exécuter le script, il est nécessaire d'installer certains modules Python qui permettent de lire les fichiers Markdown, manipuler les données et interagir avec Anki via AnkiConnect.

Installez les modules en exécutant la commande suivante :

```bash
pip install python-dotenv requests
```

### Variables d'environnement à configurer

Le script repose sur un fichier `.env` pour connaître les chemins vers les fichiers Markdown, les fichiers audio et le dossier de média d'Anki. Vous devez créer ce fichier `.env` à la racine du projet et y définir les variables suivantes :

#### Fichier `.env` :

```bash
# Chemin vers le répertoire contenant les fichiers Markdown
ROOT_DIR=/chemin/vers/les/fichiers/markdown

# Chemin vers le répertoire contenant les fichiers audio
AUDIO_DIRECTORY=/chemin/vers/les/fichiers/audio

# Chemin vers le dossier "collection.media" d'Anki
MEDIA_DIR=/chemin/vers/anki/collection.media
```

- **ROOT_DIR** : Le dossier où sont stockés les fichiers Markdown.
- **AUDIO_DIRECTORY** : Le dossier où sont stockés les fichiers audio référencés dans les notes.
- **MEDIA_DIR** : Le dossier `collection.media` d'Anki où les fichiers audio doivent être copiés.

### Installation d'Anki et d'AnkiConnect

Téléchargez et installez Anki depuis [le site officiel](https://apps.ankiweb.net/). Une fois Anki installé, vous devez installer le plugin **AnkiConnect** pour permettre au script de communiquer avec Anki.

Pour installer AnkiConnect :
1. Ouvrez Anki.
2. Allez dans **Outils > Ajouter des modules**.
3. Recherchez "AnkiConnect" et installez-le.

---

## Processus d'importation des notes

### Étapes de traitement

1. **Lecture des fichiers Markdown** : Le script parcourt chaque fichier Markdown dans le répertoire spécifié par `ROOT_DIR`. Il identifie les tableaux et extrait les données de chaque ligne.

2. **Conversion en CSV** : Chaque tableau est transformé en fichier CSV intermédiaire, ce qui permet de faciliter la manipulation des données avant leur importation dans Anki.

3. **Gestion des fichiers audio** : Si un fichier audio est référencé dans le tableau, le script vérifie sa présence dans le répertoire `AUDIO_DIRECTORY`. Si le fichier est trouvé, il est copié dans le dossier `MEDIA_DIR` d'Anki (généralement le dossier `collection.media`).

4. **Création des cartes Anki** :
   - Un **deck Anki** est créé pour chaque fichier Markdown.
   - Si des **titres de section** sont présents dans le fichier Markdown, des **sous-decks** sont créés pour organiser les cartes.
   - Chaque ligne du tableau devient une carte Anki avec :
     - Le **Mot chinois** sur le recto.
     - La **Traduction** et le **Pinyin** sur le verso.
     - Si un fichier audio est référencé, il est ajouté au verso.

### Exécution du script global

Pour lancer tout le processus d'importation, exécutez le script global dans votre terminal :

```bash
./run_scripts.bat
```

Ce script va :
1. Lire et formater les fichiers Markdown.
2. Copier les fichiers audio dans le dossier média d'Anki.
3. Créer ou mettre à jour les cartes dans Anki.

---

## Organisation des notes dans Anki

### Structure des decks

- Chaque fichier Markdown génère un **deck** principal dans Anki.
- Si des **titres de section** sont présents dans le fichier Markdown, ils sont utilisés pour créer des **sous-decks**. Par exemple, un fichier `vocabulaire.md` avec les sections `### Salutations` et `### Expressions courantes` créera les sous-decks `vocabulaire::Salutations` et `vocabulaire::Expressions courantes` dans Anki.

Cette organisation permet de garder vos cartes bien structurées dans Anki, surtout si vous avez de grandes quantités de vocabulaire à gérer.

### Modèle de note utilisé

Le script utilise le modèle **"Basique"** d'Anki, avec les champs suivants :
- **Recto** : Le mot ou l'expression en chinois.
- **Verso** : Le pinyin, la traduction, et si applicable, un fichier audio associé.

Il faut que le nom du modèle et des différentes parties des notes aient exactement les mêmes noms que ceux présentés ici.
---

## Style des cartes Anki

Si vous souhaitez définir un style personnalisé pour les champs, comme la couleur ou la taille de la police, vous pouvez le faire dans un fichier `styles.json`.

### Exemple de `styles.json`

```json
{
  "front_style": "font-size: 36px; color: #2E86C1; font-weight: bold; text-align: center;",
  "pinyin_style": "font-size: 28px; color: #FF5733; font-weight: bold;",
  "translation_style": "font-size: 22px; color: #FFFFFF;"
}
```

Le fichier `styles.json` permet de modifier l'apparence des différents champs :
- **front_style** : Style appliqué au mot chinois sur le recto de la carte.
- **pinyin_style** : Style appliqué au pinyin sur le verso de la carte.
- **translation_style** : Style appliqué à la traduction sur le verso de la carte.

Si aucun fichier de style n'est fourni, des styles par défaut seront appliqués.
