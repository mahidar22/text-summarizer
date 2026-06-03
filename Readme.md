# 🧠 SummarizeAI - Text Summarization Application

A web application that summarizes text and documents
using Machine Learning and NLP techniques.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![Scikit--learn](https://img.shields.io/badge/Scikit--learn-1.3.2-orange)
![Transformers](https://img.shields.io/badge/Transformers-4.36.2-yellow)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [How to Use](#-how-to-use)
- [API Endpoints](#-api-endpoints)
- [Supported File Types](#-supported-file-types)
- [Troubleshooting](#-troubleshooting)
- [Dependencies](#-dependencies)

---

## 📖 Overview

SummarizeAI is a text summarization web application
that supports two summarization methods:

- **Extractive** → Picks the most important sentences
  from the original text using TF-IDF + Cosine Similarity

- **Abstractive** → Generates a brand new summary
  using Facebook BART AI model via HuggingFace Transformers

---

## ✨ Features

- ✅ **Two Summarization Methods**
  - Extractive (scikit-learn + numpy)
  - Abstractive (transformers BART model)

- ✅ **Three Summary Lengths**
  - Short (1 sentence)
  - Medium (2 sentences)
  - Long (3 sentences)

- ✅ **File Upload Support**
  - PDF (.pdf)
  - Word (.doc / .docx)
  - Excel (.xls / .xlsx)
  - Text (.txt)

- ✅ **Direct Text Input**
  - Type or paste text directly

- ✅ **Live Word Count**
  - Shows word and character count in real time

- ✅ **Summary Stats**
  - Original word count
  - Summary word count
  - Reduction percentage

- ✅ **Export Options**
  - Copy to clipboard
  - Download as .txt file

- ✅ **Clean Modern UI**
  - Drag and drop file upload
  - Responsive design
  - Loading animation
  - Toast notifications

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python 3.11, Flask |
| Extractive Summarization | scikit-learn, numpy |
| Abstractive Summarization | transformers (BART), torch |
| PDF Extraction | PyMuPDF (fitz) |
| DOC Extraction | python-docx |
| Excel Extraction | openpyxl, xlrd |
| API | Flask REST API |
| CORS | flask-cors |

---

## 📁 Project Structure

```
text-summarization-app/
│
├── frontend/                   # Frontend Layer
│   ├── index.html              # Main UI page
│   ├── style.css               # Styling and layout
│   └── script.js               # API calls and UI logic
│
├── backend/                    # Backend Layer
│   ├── app.py                  # Flask server and routes
│   ├── summarizer.py           # Summarization logic
│   ├── file_extractor.py       # File text extraction
│   ├── uploads/                # Temp file storage (auto created)
│   └── requirements.txt        # Python dependencies
│
└── README.md                   # This file
```

---

## ⚙️ Installation

### Step 1 - Download Python 3.11

```
Go to → https://www.python.org/downloads/release/python-3119/
Download → Windows installer (64-bit)
File     → python-3.11.9-amd64.exe
```

> ⚠️ Make sure to check **"Add python.exe to PATH"** during installation

### Step 2 - Verify Python Installation

```powershell
py -3.11 --version
```

Expected output:
```
Python 3.11.9
```

### Step 3 - Navigate to Backend Folder

```powershell
cd "C:\Users\LENOVO\Desktop\text summarization\backend"
```

### Step 4 - Install All Dependencies

```powershell
py -3.11 -m pip install -r requirements.txt
```

### Step 5 - Verify Installation

```powershell
py -3.11 -c "
import flask
import sklearn
import numpy
import transformers
import fitz
import docx
import openpyxl
import xlrd
import torch
print('All packages installed correctly!')
"
```

Expected output:
```
All packages installed correctly!
```

---

## 🚀 How to Run

### Step 1 - Start Backend Server

```powershell
cd "C:\Users\LENOVO\Desktop\text summarization\backend"
py -3.11 app.py
```

Expected output:
```
=============================================
   SummarizeAI Backend Server Starting...
=============================================
   Upload folder : uploads
   Max file size : 10 MB
   Allowed types : PDF, DOC, DOCX, XLS, XLSX, TXT
=============================================
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 2 - Open Frontend

```
1. Open File Explorer
2. Go to → text summarization/frontend/
3. Double click → index.html
4. App opens in browser
```

### Step 3 - Verify Server is Running

Open browser and go to:
```
http://127.0.0.1:5000/health
```

Expected response:
```json
{
  "message": "SummarizeAI backend is running!",
  "status": "ok"
}
```

---

## 📖 How to Use

### Method 1 - Direct Text Input

```
1. Open index.html in browser
2. Click "Type / Paste Text" tab
3. Type or paste your text (minimum 30 words)
4. Select summarization method
   → Extractive  (faster, picks from original)
   → Abstractive (AI powered, generates new text)
5. Select summary length
   → Short  (1 sentence)
   → Medium (2 sentences)
   → Long   (3 sentences)
6. Click "Summarize Now"
7. View summary result
8. Copy or Download the summary
```

### Method 2 - File Upload

```
1. Open index.html in browser
2. Click "Upload File" tab
3. Drag & Drop file OR click to browse
4. Select summarization method
5. Select summary length
6. Click "Summarize Now"
7. View summary result
8. Copy or Download the summary
```

---

## 🔗 API Endpoints

### GET /health

```
URL    : http://127.0.0.1:5000/health
Method : GET
Use    : Check if server is running
```

Response:
```json
{
  "status" : "ok",
  "message": "SummarizeAI backend is running!"
}
```

---

### POST /summarize

```
URL    : http://127.0.0.1:5000/summarize
Method : POST
Use    : Summarize plain text
```

Request Body:
```json
{
  "text"  : "Your long text here...",
  "method": "extractive",
  "length": "medium"
}
```

Response:
```json
{
  "summary"            : "Summarized text here.",
  "original_word_count": 500,
  "summary_word_count" : 35,
  "method"             : "extractive",
  "length"             : "medium"
}
```

---

### POST /upload

```
URL    : http://127.0.0.1:5000/upload
Method : POST
Use    : Upload file and summarize
```

Request (FormData):
```
file   → uploaded file
method → extractive or abstractive
length → short, medium or long
```

Response:
```json
{
  "summary"            : "Summarized text here.",
  "original_word_count": 800,
  "summary_word_count" : 40,
  "method"             : "extractive",
  "length"             : "medium",
  "file_info": {
    "file_name": "document.pdf",
    "file_size": "245.5 KB",
    "file_type": "PDF"
  }
}
```

---

## 📄 Supported File Types

| File Type | Extension | Package |
|---|---|---|
| PDF | .pdf | PyMuPDF |
| Word Document | .docx | python-docx |
| Word Document (old) | .doc | python-docx |
| Excel | .xlsx | openpyxl |
| Excel (old) | .xls | xlrd |
| Plain Text | .txt | built-in |

---

## ❗ Troubleshooting

### pip not recognized
```powershell
py -3.11 -m pip install -r requirements.txt
```

### Port 5000 already in use
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
py -3.11 app.py
```

### Module not found
```powershell
py -3.11 -m pip install -r requirements.txt
```

### BART model slow to load
```
First time loading takes 2-5 minutes
Model is downloading (~1.6 GB)
After first load it will be cached
```

### File upload fails
```
Check file size is under 10 MB
Check file format is supported
Check backend server is running
```

### Route not found error
```
Do NOT open http://127.0.0.1:5000 in browser
Open frontend/index.html in browser instead
```

---

## 📦 Dependencies

```
flask==3.0.0
flask-cors==4.0.0
scikit-learn==1.3.2
numpy==1.26.2
transformers==4.36.2
torch==2.1.2
PyMuPDF==1.23.8
python-docx==1.1.0
openpyxl==3.1.2
xlrd==2.0.1
Werkzeug==3.0.1
```

---

## 👨‍💻 Development Notes

| Setting | Value |
|---|---|
| Backend URL | http://127.0.0.1:5000 |
| Frontend | Open index.html in browser |
| Temp uploads | backend/uploads/ (auto deleted) |
| Max file size | 10 MB |
| Min text length | 30 words |
| Debug mode | ON (turn OFF in production) |

---

## 📝 License

This project is for educational purposes.
Feel free to use and modify.

---

## 🙏 Acknowledgements

- [HuggingFace](https://huggingface.co/) - Transformers library and BART model
- [Scikit-learn](https://scikit-learn.org/) - TF-IDF vectorizer
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF text extraction
- [Flask](https://flask.palletsprojects.com/) - Python web framework

---

> Made with ❤️ using Python + Flask + Transformers + Scikit-learn
