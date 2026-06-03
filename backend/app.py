# =============================================
# app.py
# Flask Backend Server
# Routes:
#   POST /summarize  → raw text summarization
#   POST /upload     → file upload + summarization
#   GET  /health     → server health check
# =============================================

import os
import uuid

from flask            import Flask, request, jsonify
from flask_cors       import CORS

from summarizer       import summarize
from file_extractor   import extract_text, get_file_info


# =============================================
# FLASK APP SETUP
# =============================================
app = Flask(__name__)
CORS(app)   # Allow requests from frontend

# =============================================
# UPLOAD FOLDER SETUP
# Temporarily stores uploaded files
# =============================================
UPLOAD_FOLDER   = 'uploads'
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'}
MAX_FILE_SIZE   = 10 * 1024 * 1024    # 10 MB

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER']   = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


# =============================================
# UTILITY - Check allowed file extension
# =============================================
def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


# =============================================
# UTILITY - Remove file safely
# =============================================
def remove_temp_file(file_path: str):
    """Remove temporary uploaded file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass    # Silently ignore cleanup errors


# =============================================
# ROUTE 1: Health Check
# GET /health
# =============================================
@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify server is running.

    Returns:
        JSON: { status: 'ok', message: '...' }
    """
    return jsonify({
        "status" : "ok",
        "message": "SummarizeAI backend is running!"
    }), 200


# =============================================
# ROUTE 2: Summarize Plain Text
# POST /summarize
# Body: { text, method, length }
# =============================================
@app.route('/summarize', methods=['POST'])
def summarize_text():
    """
    Summarize plain text sent from frontend.

    Request Body (JSON):
        text   (str): Text to summarize
        method (str): 'extractive' or 'abstractive'
        length (str): 'short', 'medium', or 'long'

    Returns:
        JSON: {
            summary,
            original_word_count,
            summary_word_count,
            method,
            length
        }
    """

    # ---- Get JSON data ----
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received."}), 400

    # ---- Extract fields ----
    text   = data.get('text',   '').strip()
    method = data.get('method', 'extractive').strip()
    length = data.get('length', 'medium').strip()

    # ---- Validate ----
    if not text:
        return jsonify({"error": "Text field is required."}), 400

    if method not in ['extractive', 'abstractive']:
        return jsonify({"error": "Method must be 'extractive' or 'abstractive'."}), 400

    if length not in ['short', 'medium', 'long']:
        return jsonify({"error": "Length must be 'short', 'medium', or 'long'."}), 400

    # ---- Summarize ----
    try:
        result = summarize(
            text   = text,
            method = method,
            length = length
        )

        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# =============================================
# ROUTE 3: Upload File + Summarize
# POST /upload
# Body: FormData { file, method, length }
# =============================================
@app.route('/upload', methods=['POST'])
def upload_and_summarize():
    """
    Handle file upload, extract text, then summarize.

    Request Form Data:
        file   (File): Uploaded file (PDF/DOC/DOCX/XLS/XLSX/TXT)
        method (str) : 'extractive' or 'abstractive'
        length (str) : 'short', 'medium', or 'long'

    Returns:
        JSON: {
            summary,
            original_word_count,
            summary_word_count,
            method,
            length,
            file_info: { file_name, file_size, file_type }
        }
    """

    # ---- Check file in request ----
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file   = request.files['file']
    method = request.form.get('method', 'extractive').strip()
    length = request.form.get('length', 'medium').strip()

    # ---- Validate file name ----
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    # ---- Validate file extension ----
    if not is_allowed_file(file.filename):
        return jsonify({
            "error": "Unsupported file type. Allowed: PDF, DOC, DOCX, XLS, XLSX, TXT"
        }), 400

    # ---- Validate method and length ----
    if method not in ['extractive', 'abstractive']:
        return jsonify({"error": "Method must be 'extractive' or 'abstractive'."}), 400

    if length not in ['short', 'medium', 'long']:
        return jsonify({"error": "Length must be 'short', 'medium', or 'long'."}), 400

    # ---- Save file temporarily with unique name ----
    file_extension = os.path.splitext(file.filename)[1].lower()
    unique_name    = f"{uuid.uuid4().hex}{file_extension}"
    file_path      = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

    try:
        # Save uploaded file to disk
        file.save(file_path)

        # ---- Get file info ----
        file_info = get_file_info(file_path)

        # ---- Extract text from file ----
        extracted_text = extract_text(file_path)

        if not extracted_text or len(extracted_text.strip()) == 0:
            return jsonify({"error": "Could not extract text from file. File may be empty or corrupted."}), 400

        # ---- Summarize extracted text ----
        result = summarize(
            text   = extracted_text,
            method = method,
            length = length
        )

        # ---- Add file info to result ----
        result['file_info'] = file_info

        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    finally:
        # ---- Always clean up temp file ----
        remove_temp_file(file_path)


# =============================================
# ROUTE 4: Handle 404 errors
# =============================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Route not found."}), 404


# =============================================
# ROUTE 5: Handle 413 (File too large)
# =============================================
@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "File too large! Maximum size is 10 MB."}), 413


# =============================================
# RUN SERVER
# =============================================
if __name__ == '__main__':
    print("=" * 45)
    print("   SummarizeAI Backend Server Starting...")
    print("=" * 45)
    print(f"   Upload folder : {UPLOAD_FOLDER}")
    print(f"   Max file size : 10 MB")
    print(f"   Allowed types : PDF, DOC, DOCX, XLS, XLSX, TXT")
    print("=" * 45)

    app.run(
        host    = '127.0.0.1',
        port    = 5000,
        debug   = True           # Set False in production
    )