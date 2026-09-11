from rest_framework.response import Response
from rest_framework import status

def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Standardized success response helper.
    """
    return Response({
        "success": True,
        "message": message,
        "data": data if data is not None else {},
        "error": None
    }, status=status_code)

def error_response(message="An error occurred", code="ERROR", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standardized error response helper.
    """
    return Response({
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": code,
            "details": details if details is not None else str(message)
        }
    }, status=status_code)
