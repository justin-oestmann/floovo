from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
import os
from PIL import Image
import imagehash
import threading
import time
import shutil  # Importiere shutil für Dateioperationen

# Entferne die Begrenzung der maximalen Bildgröße
Image.MAX_IMAGE_PIXELS = None

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Für Flash-Nachrichten

# Ordnerpfade
MEDIA_FOLDER = "static/media"
BEHALTEN_FOLDER = "behalten"
LOESCHEN_FOLDER = "loeschen"

# Globale Variablen
analyse_ergebnisse = {}
media_files = []
analyse_abgeschlossen = False
analyse_fortschritt = 0
fehlerhafte_bilder = []
total_files = 0
analysierte_dateien = 0  # Neue Variable für die Anzahl analysierter Dateien

@app.route("/")
def index():
    """Startseite mit Ordnerstatistiken."""
    return render_template("index.html", analyse_abgeschlossen=analyse_abgeschlossen, fehlerhafte_bilder=fehlerhafte_bilder)

@app.route("/progress")
def progress():
    """Gibt den Fortschritt der Analyse zurück."""
    return jsonify({
        "progress": analyse_fortschritt,
        "analysiert": analysierte_dateien,  # Verwende die neue Variable
        "gesamt": total_files
    })

@app.route("/sort")
def sort_view():
    """Zeigt das nächste Bild oder Video an."""
    if not analyse_abgeschlossen:
        flash("Die Analyse ist noch nicht abgeschlossen. Bitte warten Sie.")
        return redirect(url_for("index"))
    if not media_files:
        return render_template("done.html")
    current_file = media_files[0]
    similar_files = analyse_ergebnisse.get(current_file, [])
    return render_template("sort.html", current_file=current_file, similar_files=similar_files)

@app.route("/sort/<filename>", methods=["POST"])
def sort_file(filename):
    """Sortiert eine Datei in den Behalten- oder Löschen-Ordner."""
    action = request.form.get("action")
    src_path = os.path.join(MEDIA_FOLDER, filename)
    if action == "behalten":
        shutil.move(src_path, os.path.join(BEHALTEN_FOLDER, filename))
    elif action == "loeschen":
        shutil.move(src_path, os.path.join(LOESCHEN_FOLDER, filename))
    media_files.remove(filename)
    return redirect(url_for("sort_view"))

@app.route("/sort/similar", methods=["POST"])
def sort_similar():
    """Sortiert ähnliche Bilder basierend auf der Auswahl."""
    selected_files = request.form.getlist("selected_files")
    for file in analyse_ergebnisse.get(media_files[0], []):
        src_path = os.path.join(MEDIA_FOLDER, file)
        if file in selected_files:
            shutil.move(src_path, os.path.join(BEHALTEN_FOLDER, file))
        else:
            shutil.move(src_path, os.path.join(LOESCHEN_FOLDER, file))
    media_files.pop(0)
    return redirect(url_for("sort_view"))

@app.route('/media/<path:filename>')
def media_file(filename):
    """Stellt Dateien aus dem static/media-Ordner bereit."""
    return send_from_directory(MEDIA_FOLDER, filename)

def get_folder_size(folder):
    """Berechnet die Größe eines Ordners in MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return round(total_size / (1024 * 1024), 2)

@app.context_processor
def inject_stats():
    """Fügt die Ordnerstatistiken zu allen Templates hinzu."""
    stats = {
        "media": {"size": get_folder_size(MEDIA_FOLDER), "count": len(os.listdir(MEDIA_FOLDER))},
        "behalten": {"size": get_folder_size(BEHALTEN_FOLDER), "count": len(os.listdir(BEHALTEN_FOLDER))},
        "loeschen": {"size": get_folder_size(LOESCHEN_FOLDER), "count": len(os.listdir(LOESCHEN_FOLDER))},
    }
    return {"stats": stats}

def analysiere_bilder():
    """Funktion zur Analyse von Bildern."""
    global analyse_ergebnisse, media_files, analyse_abgeschlossen, analyse_fortschritt, fehlerhafte_bilder, total_files, analysierte_dateien
    media_files = [f for f in os.listdir(MEDIA_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    hashes = {}
    total_files = len(media_files)  # Speichere die Gesamtanzahl der Dateien
    fehlerhafte_bilder.clear()
    analysierte_dateien = 0  # Setze die Anzahl analysierter Dateien auf 0
    for index, file in enumerate(media_files):
        file_path = os.path.join(MEDIA_FOLDER, file)
        try:
            img = Image.open(file_path)
            img.verify()  # Überprüft, ob das Bild gültig ist
            img = Image.open(file_path)  # Erneut öffnen, um es zu verarbeiten
            img_hash = imagehash.average_hash(img)
            if img_hash in hashes:
                hashes[img_hash].append(file)
            else:
                hashes[img_hash] = [file]
        except Exception as e:
            print(f"Fehler beim Analysieren von {file}: {e}")
            fehlerhafte_bilder.append(file)
        analysierte_dateien += 1  # Erhöhe die Anzahl analysierter Dateien
        analyse_fortschritt = int(((index + 1) / total_files) * 100)
        time.sleep(0.1)  # Simuliert eine Verzögerung für die Anzeige
    analyse_ergebnisse = {k: v for k, v in hashes.items() if len(v) > 1}
    analyse_abgeschlossen = True

if __name__ == "__main__":
    # Ordner erstellen, falls nicht vorhanden
    for folder in [MEDIA_FOLDER, BEHALTEN_FOLDER, LOESCHEN_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    # Analyse in einem separaten Thread starten
    analyse_thread = threading.Thread(target=analysiere_bilder, daemon=True)
    analyse_thread.start()

    # Flask-App starten
    app.run(debug=True)
