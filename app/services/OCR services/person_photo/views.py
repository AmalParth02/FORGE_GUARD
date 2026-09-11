import time
import cv2
import numpy as np
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from common.responses import success_response, error_response
from common.timer import PipelineProfiler
from person_photo.services import PersonPhotoService
from django.conf import settings

class PersonPhotoView(APIView):
    """
    POST /api/person-photo/
    Uploads document image, crops person photograph using OpenCV, saves to media storage, and returns saved image path.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        profiler = PipelineProfiler(name="Person Photo API (/api/person-photo/)")

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
            if image_np is None:
                return error_response(message="Invalid image provided", code="INVALID_IMAGE", status_code=400)
            profiler.record("Image loading", (time.perf_counter() - t0) * 1000)

            t0 = time.perf_counter()
            result = PersonPhotoService.extract_and_save_photo(
                image_np,
                settings.MEDIA_ROOT,
                media_url_prefix=settings.MEDIA_URL
            )
            profiler.record("Face crop & saving", (time.perf_counter() - t0) * 1000)

            profiler.log_summary(extra_info={"Detection method": result.get("detection_method", "")})

            return success_response(data=result, message="Person photo extracted and saved successfully")
        except Exception as e:
            return error_response(message="Person photo extraction failed", code="PHOTO_ERROR", details=str(e), status_code=500)
