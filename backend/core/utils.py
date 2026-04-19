import logging
import traceback
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response


# Configure logging
logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is None:
        # Handle Django exceptions
        logger.error(f"Unhandled exception: {exc}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return Response({
            'status': 'error',
            'message': 'An internal server error occurred',
            'error_code': 'INTERNAL_ERROR',
            'details': str(exc) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Customize the response
    custom_response_data = {
        'status': 'error',
        'message': response.data.get('detail', 'An error occurred'),
        'error_code': getattr(exc, 'default_code', 'UNKNOWN_ERROR'),
    }
    
    if settings.DEBUG:
        custom_response_data['details'] = response.data
    
    response.data = custom_response_data
    return response


class APIError(Exception):
    """Base API exception class"""
    def __init__(self, message, error_code=None, status_code=400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error exception"""
    def __init__(self, message, field=None):
        super().__init__(message, 'VALIDATION_ERROR', 400)
        self.field = field


class AuthenticationError(APIError):
    """Authentication error exception"""
    def __init__(self, message='Authentication failed'):
        super().__init__(message, 'AUTH_ERROR', 401)


class AuthorizationError(APIError):
    """Authorization error exception"""
    def __init__(self, message='Access denied'):
        super().__init__(message, 'AUTHZ_ERROR', 403)


class NotFoundError(APIError):
    """Not found error exception"""
    def __init__(self, message='Resource not found'):
        super().__init__(message, 'NOT_FOUND', 404)


class ConflictError(APIError):
    """Conflict error exception"""
    def __init__(self, message='Resource conflict'):
        super().__init__(message, 'CONFLICT', 409)


class RateLimitError(APIError):
    """Rate limit error exception"""
    def __init__(self, message='Rate limit exceeded'):
        super().__init__(message, 'RATE_LIMIT', 429)


class ServiceError(APIError):
    """Service error exception"""
    def __init__(self, message='Service unavailable'):
        super().__init__(message, 'SERVICE_ERROR', 503)


def log_api_request(request, response, duration=None):
    """Log API request details"""
    log_data = {
        'method': request.method,
        'path': request.path,
        'status_code': response.status_code,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'ip_address': get_client_ip(request),
    }
    
    if duration:
        log_data['duration_ms'] = round(duration * 1000, 2)
    
    if response.status_code >= 400:
        logger.warning(f"API Error: {log_data}")
    else:
        logger.info(f"API Request: {log_data}")


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_required_fields(data, required_fields):
    """Validate required fields in request data"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            field=missing_fields[0] if missing_fields else None
        )


def sanitize_input(data):
    """Sanitize input data"""
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        # Basic sanitization - strip whitespace and remove potentially harmful characters
        return data.strip().replace('<script>', '').replace('</script>', '')
    else:
        return data


class AuditLogger:
    """Audit logging utility"""
    
    @staticmethod
    def log_user_action(user, action, details=None):
        """Log user actions"""
        logger.info(f"User Action: {user.username} ({user.id}) - {action}")
        if details:
            logger.info(f"Details: {details}")
    
    @staticmethod
    def log_system_event(event, details=None):
        """Log system events"""
        logger.info(f"System Event: {event}")
        if details:
            logger.info(f"Details: {details}")
    
    @staticmethod
    def log_security_event(event, details=None):
        """Log security events"""
        logger.warning(f"Security Event: {event}")
        if details:
            logger.warning(f"Details: {details}")


def handle_database_error(operation):
    """Decorator to handle database errors"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Database error during {operation}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise ServiceError(f"Database operation failed: {operation}")
        return wrapper
    return decorator


def cache_with_timeout(timeout=300):
    """Simple caching decorator"""
    cache = {}
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            cache_key = str(args) + str(kwargs)
            current_time = time.time()
            
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < timeout:
                    return result
            
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            return result
        return wrapper
    return decorator


# Import settings for debug mode
from django.conf import settings
