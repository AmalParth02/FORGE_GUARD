from rest_framework.views import APIView
from common.responses import success_response, error_response
from text_extraction.services import TextExtractionService

class TextExtractionView(APIView):
    """
    POST /api/extract/
    Accepts text payload and uses Regex patterns to extract structured fields (Name, DOB, Aadhaar, PAN, Passport, etc.).
    """
    def post(self, request, *args, **kwargs):
        text = request.data.get('text', '')
        if not text or not text.strip():
            return error_response(
                message="No 'text' string provided in request body.",
                code="MISSING_TEXT",
                status_code=400
            )

        try:
            result = TextExtractionService.extract_fields(text)
            return success_response(data=result, message="Structured text fields extracted successfully")
        except Exception as e:
            return error_response(message="Text extraction failed", code="EXTRACTION_ERROR", details=str(e), status_code=500)
