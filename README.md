# Smart India Hackathon (SIH) - OCR & Data Extraction Backend

A simple, modular, and beginner-friendly **Django REST Framework (DRF)** backend for document OCR, structured regex field extraction, PassportEye MRZ parsing, and OpenCV person photograph extraction.

---

## 📁 Project Architecture & Modular Folder Structure

```
D:\SIH\backend\
├── venv\                       # Python Virtual Environment
├── manage.py                   # Django Management CLI
├── requirements.txt            # Python Dependencies
├── README.md                   # Project Documentation
│
├── config\                     # Django Project Settings & Core Routing
│   ├── settings.py             # DRF, Apps & Media URLs setup
│   ├── urls.py                 # Root URL router (/api/)
│   ├── wsgi.py
│   └── asgi.py
│
├── common\                     # Standard API Response & Exception Handler
│   ├── responses.py            # success_response() & error_response()
│   └── exceptions.py           # Custom DRF exception handler
│
├── preprocessing\              # Image Preprocessing Module (OpenCV)
│   └── services.py             # Noise removal, deskewing, thresholding
│
├── ocr\                        # Document OCR Module (PaddleOCR)
│   ├── services.py             # PaddleOCR engine runner
│   ├── views.py                # POST /api/ocr/ & POST /api/process-document/
│   └── urls.py
│
├── text_extraction\            # Regex Field Extractor Module
│   ├── regex_patterns.py       # Compiled Regex patterns (Name, DOB, Aadhaar, PAN, Passport, etc.)
│   ├── services.py             # Text field parsing logic
│   ├── views.py                # POST /api/extract/
│   └── urls.py
│
├── mrz\                        # MRZ Passport Parser Module (PassportEye)
│   ├── services.py             # PassportEye MRZ scanner & parser
│   ├── views.py                # POST /api/mrz/
│   └── urls.py
│
├── person_photo\               # Face / Person Photo Crop Module (OpenCV)
│   ├── services.py             # Face detection, crop & media save logic
│   ├── views.py                # POST /api/person-photo/
│   └── urls.py
│
└── media\                      # Uploads and Extracted Files Storage
    ├── temp\                   # Temporary file uploads
    └── person_photos\          # Extracted person photographs
```

---

## 🛠️ Step-by-Step Setup Guide

### 1. Open Terminal & Navigate to Project Folder
```powershell
d:
cd D:\SIH\backend
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
```

### 3. Activate Virtual Environment
- **Windows PowerShell**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows Command Prompt (cmd)**:
  ```cmd
  venv\Scripts\activate.bat
  ```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Run Database Migrations
```powershell
python manage.py migrate
```

### 6. Start the Django Server
```powershell
python manage.py runserver
```
The server will start at: `http://127.0.0.1:8000/`

---

## 🌐 Uniform API Response Schema

Every API endpoint adheres strictly to the following unified response structure:

### Success Response Example (HTTP 200/201)
```json
{
    "success": true,
    "message": "OCR processing completed successfully",
    "data": {
        "text": "GOVERNMENT OF INDIA\nName: RAMESH KUMAR\nDOB: 15/08/1995",
        "line_count": 3
    },
    "error": null
}
```

### Error Response Example (HTTP 400/500)
```json
{
    "success": false,
    "message": "No image file provided in request",
    "data": null,
    "error": {
        "code": "MISSING_FILE",
        "details": "Please attach 'image' or 'file' parameter."
    }
}
```

---

## 🚀 API Endpoint Documentation & Examples

### 1. Document OCR API
- **Endpoint**: `POST /api/ocr/`
- **Description**: Uploads a document scan, applies OpenCV noise removal & deskewing, runs PaddleOCR, and returns detected text.
- **Content-Type**: `multipart/form-data`
- **Parameters**: `image` (file)
- **cURL Request**:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/ocr/ -F "image=@sample_aadhaar.jpg"
  ```
- **Example Response**:
  ```json
  {
      "success": true,
      "message": "OCR processing completed successfully",
      "data": {
          "text": "GOVERNMENT OF INDIA\nName: AARAV PATEL\nDOB: 10/05/1992",
          "line_count": 3,
          "preprocessed": true
      },
      "error": null
  }
  ```

---

### 2. Structured Field Extraction API (Regex)
- **Endpoint**: `POST /api/extract/`
- **Description**: Receives OCR raw text string and uses Regex to extract structured key-value fields.
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
      "text": "GOVERNMENT OF INDIA\nName: AARAV PATEL\nDOB: 10/05/1992\nGender: Male\nAadhaar: 9876 5432 1012\nPIN: 400001"
  }
  ```
- **Example Response**:
  ```json
  {
      "success": true,
      "message": "Structured text fields extracted successfully",
      "data": {
          "document_type": "AADHAAR_CARD",
          "extracted_fields": {
              "name": "AARAV PATEL",
              "dob": "10/05/1992",
              "gender": "MALE",
              "aadhaar_number": "987654321012",
              "pincode": "400001"
          }
      },
      "error": null
  }
  ```

---

### 3. Passport MRZ Parser API (PassportEye)
- **Endpoint**: `POST /api/mrz/`
- **Description**: Uploads passport scan, reads Machine Readable Zone (MRZ), and returns parsed structured fields.
- **Content-Type**: `multipart/form-data`
- **Parameters**: `image` (file)
- **Example Response**:
  ```json
  {
      "success": true,
      "message": "MRZ parsing completed successfully",
      "data": {
          "mrz_found": true,
          "fields": {
              "document_type": "P",
              "country": "IND",
              "surname": "SHARMA",
              "names": "PRIYA",
              "number": "J1234567",
              "nationality": "IND",
              "date_of_birth": "981124",
              "sex": "F"
          },
          "valid_score": 100
      },
      "error": null
  }
  ```

---

### 4. Person Photo Extraction API (OpenCV Face Detector)
- **Endpoint**: `POST /api/person-photo/`
- **Description**: Detects, crops, and saves the person's photo from document/passport scan into `media/person_photos/`.
- **Content-Type**: `multipart/form-data`
- **Parameters**: `image` (file)
- **Example Response**:
  ```json
  {
      "success": true,
      "message": "Person photo extracted and saved successfully",
      "data": {
          "filename": "person_1788703270_ee87eb.jpg",
          "saved_path": "D:\\SIH\\backend\\media\\person_photos\\person_1788703270_ee87eb.jpg",
          "photo_url": "/media/person_photos/person_1788703270_ee87eb.jpg",
          "detection_method": "FACE_CASCADE_DETECTED"
      },
      "error": null
  }
  ```

---

### 5. All-in-One Document Pipeline API
- **Endpoint**: `POST /api/process-document/`
- **Description**: Runs full pipeline (Preprocessing -> PaddleOCR -> Regex Extraction -> MRZ Parsing -> Photo Crop) in a single request.
- **Content-Type**: `multipart/form-data`
- **Parameters**: `image` (file)

---

## 🧪 Testing the APIs with Python

You can easily test all endpoints using Python `requests`:

```python
import requests

url = "http://127.0.0.1:8000/api/extract/"
payload = {
    "text": "Name: PRIYA SHARMA\nDOB: 12/03/1997\nPAN: ABCDE1234F"
}

response = requests.post(url, json=payload)
print(response.json())
```
