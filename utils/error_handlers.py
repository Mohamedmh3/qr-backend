"""
Comprehensive error handling and logging utilities.
"""

import logging
import traceback
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
import json

logger = logging.getLogger(__name__)


class APIError(Exception):
    """
    Custom API error class for consistent error handling.
    """
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


def handle_api_errors(func):
    """
    Decorator to handle API errors consistently.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            logger.error(f"API Error: {e.message} (Code: {e.error_code})")
            return Response({
                'error': e.message,
                'error_code': e.error_code,
                'status': 'error'
            }, status=e.status_code)
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            if settings.DEBUG:
                return Response({
                    'error': f'Internal server error: {str(e)}',
                    'error_code': 'INTERNAL_ERROR',
                    'status': 'error',
                    'debug_info': traceback.format_exc()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'error': 'Internal server error',
                    'error_code': 'INTERNAL_ERROR',
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return wrapper


def log_api_request(func):
    """
    Decorator to log API requests and responses.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[1] if len(args) > 1 else None
        
        if request:
            logger.info(f"API Request: {request.method} {request.path}")
            logger.debug(f"Request data: {request.data if hasattr(request, 'data') else 'No data'}")
        
        try:
            response = func(*args, **kwargs)
            
            if hasattr(response, 'status_code'):
                logger.info(f"API Response: {response.status_code}")
            
            return response
        except Exception as e:
            logger.error(f"API Error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper


def validate_required_fields(data, required_fields):
    """
    Validate that required fields are present in the data.
    
    Args:
        data (dict): Data to validate
        required_fields (list): List of required field names
        
    Raises:
        APIError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        raise APIError(
            f"Missing required fields: {', '.join(missing_fields)}",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code='MISSING_FIELDS'
        )


def validate_email_format(email):
    """
    Validate email format.
    
    Args:
        email (str): Email to validate
        
    Raises:
        APIError: If email format is invalid
    """
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise APIError(
            "Invalid email format",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code='INVALID_EMAIL'
        )


def validate_password_strength(password):
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
        
    Raises:
        APIError: If password doesn't meet strength requirements
    """
    if len(password) < 8:
        raise APIError(
            "Password must be at least 8 characters long",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code='WEAK_PASSWORD'
        )
    
    if not any(c.isupper() for c in password):
        raise APIError(
            "Password must contain at least one uppercase letter",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code='WEAK_PASSWORD'
        )
    
    if not any(c.islower() for c in password):
        raise APIError(
            "Password must contain at least one lowercase letter",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code='WEAK_PASSWORD'
        )
    
    if not any(c.isdigit() for c in password):
        raise APIError(
            "Password must contain at least one digit",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code='WEAK_PASSWORD'
        )


def log_database_operation(operation, collection, query=None, result=None):
    """
    Log database operations for debugging and monitoring.
    
    Args:
        operation (str): Type of operation (find, insert, update, delete)
        collection (str): Collection name
        query (dict): Query used
        result: Result of the operation
    """
    logger.info(f"Database {operation} on {collection}")
    
    if query:
        logger.debug(f"Query: {json.dumps(query, default=str)}")
    
    if result:
        logger.debug(f"Result: {json.dumps(result, default=str)}")


def create_error_response(message, status_code=status.HTTP_400_BAD_REQUEST, error_code=None):
    """
    Create a standardized error response.
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        error_code (str): Custom error code
        
    Returns:
        Response: Standardized error response
    """
    return Response({
        'error': message,
        'error_code': error_code,
        'status': 'error'
    }, status=status_code)


def create_success_response(data, message="Success", status_code=status.HTTP_200_OK):
    """
    Create a standardized success response.
    
    Args:
        data (dict): Response data
        message (str): Success message
        status_code (int): HTTP status code
        
    Returns:
        Response: Standardized success response
    """
    return Response({
        'data': data,
        'message': message,
        'status': 'success'
    }, status=status_code)







