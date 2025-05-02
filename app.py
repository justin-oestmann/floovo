from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import imagehash
import threading
import time
import shutil  # Importiere shutil für Dateioperationen
import logging  # Importiere das Logging-Modul

# Entferne die Begrenzung der maximalen Bildgröße
Image.MAX_IMAGE_PIXELS = None

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Für Flash-Nachrichten

# Feste Ordnerpfade
MEDIA_FOLDER = "static/media"
BEHALTEN_FOLDER = "behalten"
LOESCHEN_FOLDER = "loeschen"

# Erlaubte Dateitypen für den Upload (include mp4 for videos)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4'}

# Globale Variablen
analyse_ergebnisse = {}
media_files = []
analyse_abgeschlossen = False
analyse_fortschritt = 0
fehlerhafte_bilder = []
total_files = 0
analysierte_dateien = 0  # Neue Variable für die Anzahl analysierter Dateien

def allowed_file(filename):
    """Überprüft, ob die Datei einen erlaubten Typ hat."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    """Home-Seite mit Ordnerstatistiken."""
    if not os.listdir(MEDIA_FOLDER):
        flash("Bitte laden Sie zuerst Dateien in Floovo hoch!", "info")
    return render_template(
        "index.html",
        analyse_abgeschlossen=analyse_abgeschlossen,
        fehlerhafte_bilder=fehlerhafte_bilder,
        analyse_fortschritt=analyse_fortschritt,
        total_files=total_files,
    )

@app.route("/upload", methods=["GET", "POST"])
def upload_files():
    """Seite zum Hochladen von Dateien."""
    global analyse_abgeschlossen, analyse_fortschritt

    if analyse_fortschritt > 0 and not analyse_abgeschlossen:
        flash("Die Analyse läuft. Sie können keine Dateien mehr hochladen.", "info")
        return redirect(url_for("home"))

    if request.method == "POST":
        if 'files[]' not in request.files:
            flash("Keine Dateien ausgewählt!", "danger")
            return redirect(request.url)

        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(MEDIA_FOLDER, filename))

        flash("Dateien erfolgreich in Floovo hochgeladen!", "success")
        return redirect(request.url)

    existing_files = os.listdir(MEDIA_FOLDER)
    return render_template(
        "upload.html",
        existing_files=existing_files,
        analyse_fortschritt=analyse_fortschritt,
        analyse_abgeschlossen=analyse_abgeschlossen,
    )

@app.route("/start_analysis", methods=["POST"])
def start_analysis():
    """Manually starts the analysis."""
    global analyse_abgeschlossen, analyse_fortschritt, analysierte_dateien, total_files

    # Reset analysis variables
    analyse_abgeschlossen = False
    analyse_fortschritt = 0
    analysierte_dateien = 0
    total_files = 0

    # Start analysis in a separate thread
    analyse_thread = threading.Thread(target=analysiere_bilder, daemon=True)
    analyse_thread.start()

    flash("Analysis started!", "info")
    return redirect(url_for("home"))

@app.route("/progress")
def progress():
    """Returns the progress of the analysis."""
    # Ensure progress reflects completion when analysis is done
    if analyse_abgeschlossen:
        return jsonify({
            "progress": 100,
            "analyzed": total_files,
            "total": total_files
        })
    return jsonify({
        "progress": analyse_fortschritt,
        "analyzed": analysierte_dateien,
        "total": total_files
    })

@app.route("/sort")
def sort_view():
    """Displays the next image, video, or group of similar images."""
    if not analyse_abgeschlossen:
        flash("The analysis is not yet complete. Please wait.")
        return redirect(url_for("home"))
    
    # Ensure media_files includes both images and videos
    if not media_files:
        return render_template("done.html")
    
    current_file = media_files[0]
    
    # Check if the current file is a video
    if current_file.lower().endswith('.mp4'):
        return render_template("sort.html", current_file=current_file, similar_files=[])

    # Search for the group to which the current image belongs
    for group_files in analyse_ergebnisse.values():
        if current_file in group_files:
            return render_template("sort.html", current_file=None, similar_files=group_files)
    
    # If no group is found, display the single image
    return render_template("sort.html", current_file=current_file, similar_files=[])

@app.route("/sort/<filename>", methods=["POST"])
def sort_file(filename):
    """Sorts a file into the Keep or Delete folder."""
    action = request.form.get("action")
    src_path = os.path.join(MEDIA_FOLDER, filename)
    if action == "behalten":
        shutil.move(src_path, os.path.join(BEHALTEN_FOLDER, filename))
    elif action == "loeschen":
        shutil.move(src_path, os.path.join(LOESCHEN_FOLDER, filename))
    
    # Remove the file from media_files after sorting
    if filename in media_files:
        media_files.remove(filename)
    
    return redirect(url_for("sort_view"))

@app.route("/sort/similar", methods=["POST"])
def sort_similar():
    """Sortiert ähnliche Bilder basierend auf der Auswahl und wechselt zur nächsten Gruppe."""
    selected_files = request.form.getlist("selected_files")
    current_group = None

    # Find the group for the current file
    for group_files in analyse_ergebnisse.values():
        if any(file in media_files for file in group_files):
            current_group = group_files
            break

    if current_group:
        for file in current_group:
            src_path = os.path.join(MEDIA_FOLDER, file)
            if file in selected_files:
                shutil.move(src_path, os.path.join(BEHALTEN_FOLDER, file))
            else:
                shutil.move(src_path, os.path.join(LOESCHEN_FOLDER, file))
        
        # Remove all files in the current group from media_files
        media_files[:] = [file for file in media_files if file not in current_group]

    # Redirect to the next group or finish sorting
    if media_files:
        return redirect(url_for("sort_view"))
    else:
        return redirect(url_for("done"))

@app.route('/media/<path:filename>')
def media_file(filename):
    """Stellt Dateien aus dem media-Ordner bereit."""
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analysiere_bilder():
    """Function to analyze images."""
    global analyse_ergebnisse, media_files, analyse_abgeschlossen, analyse_fortschritt, fehlerhafte_bilder, total_files, analysierte_dateien
    # Include both images and videos in media_files
    media_files = [f for f in os.listdir(MEDIA_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4'))]
    media_files = [f for f in media_files if os.path.isfile(os.path.join(MEDIA_FOLDER, f))]  # Ensure only files are included
    if not media_files:
        logging.info("No media files found in the media folder.")
        analyse_abgeschlossen = True
        analyse_fortschritt = 100
        return

    hashes = {}
    total_files = len(media_files)  # Set the total number of files
    fehlerhafte_bilder.clear()
    analysierte_dateien = 0  # Reset the number of analyzed files
    similarity_threshold = 18.5  # Less strict threshold for similar images

    logging.info(f"Starting analysis for {total_files} files.")

    for index, file in enumerate(media_files):
        if file.lower().endswith('.mp4'):
            # Skip analysis for videos but keep them in media_files
            logging.info(f"Skipping analysis for video file '{file}'.")
            continue

        file_path = os.path.join(MEDIA_FOLDER, file)
        try:
            with Image.open(file_path) as img:  # Ensure the file is properly closed after use
                img.verify()
                img = Image.open(file_path)

                # Combine multiple hash algorithms
                img_hashes = {
                    "phash": imagehash.phash(img),
                    "dhash": imagehash.dhash(img),
                    "average_hash": imagehash.average_hash(img)
                }
                found_similar = False

                for existing_hashes in hashes.values():
                    # Compare all hashes with a combined threshold
                    if all(abs(img_hashes[hash_type] - existing_hashes[hash_type]) <= similarity_threshold
                           for hash_type in img_hashes):
                        existing_hashes["files"].append(file)
                        logging.info(f"Image '{file}' grouped with '{existing_hashes['files'][0]}'.")
                        found_similar = True
                        break

                if not found_similar:
                    hashes[tuple(img_hashes.values())] = {
                        "phash": img_hashes["phash"],
                        "dhash": img_hashes["dhash"],
                        "average_hash": img_hashes["average_hash"],
                        "files": [file]
                    }
                    logging.info(f"Image '{file}' added as a new group.")
        except Exception as e:
            logging.error(f"Error analyzing '{file}': {e}")
            fehlerhafte_bilder.append(file)

        analysierte_dateien += 1  # Increment the number of analyzed files
        analyse_fortschritt = int(((index + 1) / total_files) * 100)  # Calculate progress
        time.sleep(0.1)  # Simulate a delay

    # If only videos remain, mark the analysis as complete
    if all(file.lower().endswith('.mp4') for file in media_files):
        analyse_fortschritt = 100
        logging.info("Analysis complete. Only videos remain.")
    
    # Extract groups with more than one image
    analyse_ergebnisse = {k: v["files"] for k, v in hashes.items() if len(v["files"]) > 1}
    logging.info(f"Analysis complete. Found {len(analyse_ergebnisse)} groups with similar images.")
    analyse_abgeschlossen = True

@app.route("/dev/groups", methods=["GET"])
def dev_groups():
    """Gibt die gruppierten Bilder als JSON zurück (nur für Entwicklungszwecke)."""
    if app.debug:  # Nur verfügbar, wenn die App im Debug-Modus läuft
        return jsonify({
            "groups": {str(hash_key): files for hash_key, files in analyse_ergebnisse.items()}
        })
    else:
        return jsonify({"error": "Diese Funktion ist nur im Debug-Modus verfügbar."}), 403

@app.route("/dev/media_files", methods=["GET"])
def dev_media_files():
    """Provides the list of media files as JSON (for development purposes only)."""
    if app.debug:  # Only available when the app is in debug mode
        return jsonify({"media_files": media_files})
    else:
        return jsonify({"error": "This endpoint is only available in debug mode."}), 403

@app.route("/done")
def done():
    """Zeigt die Abschlussseite an, wenn alle Dateien sortiert wurden."""
    return render_template("done.html")

if __name__ == "__main__":
    for folder in [MEDIA_FOLDER, BEHALTEN_FOLDER, LOESCHEN_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    app.run(debug=True)
