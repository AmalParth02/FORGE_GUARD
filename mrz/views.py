import time
import cv2
import numpy as np
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from common.responses import success_response, error_response
from common.timer import PipelineProfiler
from mrz.services import MRZService

class MRZView(APIView):
    """
    POST /api/mrz/
    Uploads passport/document image, parses MRZ, and returns structured data.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        profiler = PipelineProfiler(name="MRZ API (/api/mrz/)")

        file_obj = request.FILES.get('image') or request.FILES.get('file')
        if not file_obj:
            return error_response(
                message="No image file provided in request. Please attach 'image' or 'file'.",
                code="MISSING_FILE",
                status_code=400
            )

        try:
            t0 = time.perf_counter()
            image_bytes = file_obj.read()
            image_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            profiler.record("Image loading", (time.perf_counter() - t0) * 1000)

            t0 = time.perf_counter()
            # Also attempt fast OCR-based parse if available or fallback
            from ocr.services import OCRService
            ocr_res = OCRService.extract_text(image_np, apply_preprocessing=False)
            result = MRZService.parse_mrz(image_input=None, ocr_text=ocr_res.get("text", ""), lines=ocr_res.get("lines", []))
            profiler.record("MRZ parsing", (time.perf_counter() - t0) * 1000)

            profiler.log_summary(extra_info={"MRZ detected": result.get("mrz_found", False)})

            return success_response(data=result, message="MRZ parsing completed successfully")
        except Exception as e:
            return error_response(message="MRZ parsing failed", code="MRZ_ERROR", details=str(e), status_code=500)
