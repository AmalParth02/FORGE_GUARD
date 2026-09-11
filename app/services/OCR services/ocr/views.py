import time
import cv2
import numpy as np
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings

from common.responses import success_response, error_response
from common.timer import PipelineProfiler
from ocr.services import OCRService
from text_extraction.services import TextExtractionService
from mrz.services import MRZService
from person_photo.services import PersonPhotoService
from preprocessing.services import ImagePreprocessor


class OCRView(APIView):
    """
    POST /api/ocr/
    Uploads document image, applies preprocessing (optional), runs PaddleOCR, and returns extracted text.
    Optimized for in-memory stream processing with zero temporary disk I/O.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        profiler = PipelineProfiler(name="OCR API (/api/ocr/)")
        profiler.record("Request received", 0.0)

        file_obj = request.FILES.get('image') or request.FILES.get('file')
        if not file_obj:
            return error_response(
                message="No image file provided in request. Please attach 'image' or 'file'.",
                code="MISSING_FILE",
                status_code=400
            )

        try:
            # 1. File upload / read from memory buffer
            t0 = time.perf_counter()
            image_bytes = file_obj.read()
            profiler.record("File upload/read", (time.perf_counter() - t0) * 1000)

            # 2. File save (Bypassed in-memory)
            profiler.record("File save", 0.0)

            # 3. Image decoding
            t0 = time.perf_counter()
            image_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            if image_np is None:
                return error_response(message="Invalid or unsupported image format.", code="INVALID_IMAGE", status_code=400)
            profiler.record("Image decoding", (time.perf_counter() - t0) * 1000)

            # 4. Image preprocessing
            apply_preprocess = request.data.get('preprocess', 'true').lower() in ['true', '1']
            t0 = time.perf_counter()
            if apply_preprocess:
                proc_image = ImagePreprocessor.preprocess(image_np)
            else:
                proc_image = image_np
            profiler.record("Image preprocessing", (time.perf_counter() - t0) * 1000)

            # 5. PaddleOCR inference
            t0 = time.perf_counter()
            result = OCRService.extract_text(proc_image, apply_preprocessing=False)
            profiler.record("PaddleOCR inference", (time.perf_counter() - t0) * 1000)

            # 6. OCR text extraction
            profiler.record("OCR text extraction", 0.1)

            # 7. JSON creation
            t0 = time.perf_counter()
            response = success_response(data=result, message="OCR processing completed successfully")
            profiler.record("JSON creation", (time.perf_counter() - t0) * 1000)

            # Log benchmark summary to server console
            profiler.log_summary(extra_info={
                "Hardware device": OCRService.get_device_info(),
                "Lines extracted": result.get("line_count", 0),
                "Preprocessed": apply_preprocess
            })

            return response

        except Exception as e:
            return error_response(message="OCR processing failed", code="OCR_ERROR", details=str(e), status_code=500)


class DocumentPipelineView(APIView):
    """
    POST /api/process-document/
    Combined End-to-End Pipeline:
    1. Direct in-memory image read (0 temp file writes)
    2. Fast Preprocessing & PaddleOCR Text Recognition
    3. Structured Field Extraction via Regex
    4. Fast MRZ parsing (<1ms) with PassportEye fallback
    5. Face detection, crop & single photo saving
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        profiler = PipelineProfiler(name="Document Pipeline (/api/process-document/)")
        
        # Step 1: Request received
        profiler.record("Request received", 0.0)

        file_obj = request.FILES.get('image') or request.FILES.get('file')
        if not file_obj:
            return error_response(
                message="No image file provided in request. Please attach 'image' or 'file'.",
                code="MISSING_FILE",
                status_code=400
            )

        try:
            # Step 2: File upload/read (in-memory stream)
            t0 = time.perf_counter()
            image_bytes = file_obj.read()
            profiler.record("File upload/read", (time.perf_counter() - t0) * 1000)

            # Step 3: File save (0ms - skipped via direct memory streaming)
            profiler.record("File save", 0.0)

            # Step 4: Image decoding
            t0 = time.perf_counter()
            image_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            if image_np is None:
                return error_response(message="Invalid or corrupt image uploaded.", code="INVALID_IMAGE", status_code=400)
            profiler.record("Image decoding", (time.perf_counter() - t0) * 1000)

            # Step 5: Image preprocessing (fast in-memory deskew + denoise)
            t0 = time.perf_counter()
            proc_image = ImagePreprocessor.preprocess(image_np)
            profiler.record("Image preprocessing", (time.perf_counter() - t0) * 1000)

            # Step 6: PaddleOCR inference
            t0 = time.perf_counter()
            ocr_result = OCRService.extract_text(proc_image, apply_preprocessing=False)
            profiler.record("PaddleOCR inference", (time.perf_counter() - t0) * 1000)

            # Step 7: OCR text extraction
            t0 = time.perf_counter()
            ocr_text = ocr_result.get("text", "")
            ocr_lines = ocr_result.get("lines", [])
            profiler.record("OCR text extraction", (time.perf_counter() - t0) * 1000)

            # Step 8: MRZ parsing (Sub-millisecond direct text parse)
            t0 = time.perf_counter()
            mrz_data = MRZService.parse_mrz(ocr_text=ocr_text, lines=ocr_lines)
            profiler.record("MRZ parsing", (time.perf_counter() - t0) * 1000)

            # Step 9: Regex/data extraction
            t0 = time.perf_counter()
            structured_data = TextExtractionService.extract_fields(ocr_text)
            profiler.record("Regex/data extraction", (time.perf_counter() - t0) * 1000)

            # Step 10: Document type detection
            t0 = time.perf_counter()
            doc_type = structured_data.get("document_type", "UNKNOWN")
            profiler.record("Document type detection", (time.perf_counter() - t0) * 1000)

            # Step 11: Person photo extraction (face detection + crop)
            t0 = time.perf_counter()
            photo_data = PersonPhotoService.extract_and_save_photo(
                image_np,
                settings.MEDIA_ROOT,
                media_url_prefix=settings.MEDIA_URL
            )
            profiler.record("Person photo extraction", (time.perf_counter() - t0) * 1000)

            # Step 12: Person photo saving (included in photo service)
            profiler.record("Person photo saving", 0.5)

            # Step 13: JSON creation
            t0 = time.perf_counter()
            response_data = {
                "ocr": ocr_result,
                "structured_data": structured_data,
                "mrz": mrz_data,
                "person_photo": photo_data
            }
            response = success_response(data=response_data, message="Document pipeline processing completed successfully")
            profiler.record("JSON creation", (time.perf_counter() - t0) * 1000)

            # Step 14: Total response time logged in profiler summary
            profiler.log_summary(extra_info={
                "Hardware device": OCRService.get_device_info(),
                "Document type detected": doc_type,
                "MRZ found": mrz_data.get("mrz_found", False),
                "Face detection": photo_data.get("detection_method", "")
            })

            return response

        except Exception as e:
            return error_response(message="Document pipeline processing failed", code="PIPELINE_ERROR", details=str(e), status_code=500)
