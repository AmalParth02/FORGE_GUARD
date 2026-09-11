from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler to ensure ALL DRF exceptions adhere to standard response schema.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "message": "Request validation or API error",
            "data": None,
            "error": {
                "code": "API_ERROR",
                "details": response.data
            }
        }
        return Response(custom_data, status=response.status_code)

    return Response({
        "success": False,
        "message": "Internal server error",
        "data": None,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "details": str(exc)
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
