from decouple import config
from pathlib import Path
import os


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment-specific settings
ENVIRONMENT = config('ENVIRONMENT', default='development')

# Database Configuration
DATABASE_CONFIG = {
    'development': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'production': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Security Configuration
SECURITY_CONFIG = {
    'development': {
        'DEBUG': True,
        'ALLOWED_HOSTS': ['*'],
        'SECRET_KEY': 'django-insecure-development-key-change-in-production',
    },
    'production': {
        'DEBUG': False,
        'ALLOWED_HOSTS': config('ALLOWED_HOSTS', default='').split(','),
        'SECRET_KEY': config('SECRET_KEY'),
        'SECURE_SSL_REDIRECT': True,
        'SECURE_HSTS_SECONDS': 31536000,
        'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
        'SECURE_HSTS_PRELOAD': True,
    }
}

# Email Configuration
EMAIL_CONFIG = {
    'development': {
        'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
    'production': {
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'EMAIL_HOST': config('EMAIL_HOST'),
        'EMAIL_PORT': config('EMAIL_PORT', default=587, cast=int),
        'EMAIL_USE_TLS': config('EMAIL_USE_TLS', default=True, cast=bool),
        'EMAIL_HOST_USER': config('EMAIL_HOST_USER'),
        'EMAIL_HOST_PASSWORD': config('EMAIL_HOST_PASSWORD'),
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'development': {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': BASE_DIR / 'debug.log',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'core': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    },
    'production': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': '/var/log/swasthya/django.log',
                'maxBytes': 1024*1024*15,  # 15MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'mail_admins': {
                'class': 'django.utils.log.AdminEmailHandler',
                'level': 'ERROR',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'mail_admins'],
                'level': 'INFO',
                'propagate': True,
            },
            'core': {
                'handlers': ['file', 'mail_admins'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
}

# Cache Configuration
CACHE_CONFIG = {
    'development': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    'production': {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        }
    }
}

# API Configuration
API_CONFIG = {
    'development': {
        'CORS_ALLOWED_ORIGINS': [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        'CORS_ALLOW_CREDENTIALS': True,
        'RATE_LIMIT_ENABLE': False,
    },
    'production': {
        'CORS_ALLOWED_ORIGINS': config('CORS_ALLOWED_ORIGINS', default='').split(','),
        'CORS_ALLOW_CREDENTIALS': True,
        'RATE_LIMIT_ENABLE': True,
        'RATE_LIMIT_REQUESTS': config('RATE_LIMIT_REQUESTS', default=100, cast=int),
        'RATE_LIMIT_WINDOW': config('RATE_LIMIT_WINDOW', default=3600, cast=int),  # 1 hour
    }
}

# ML Model Configuration
ML_CONFIG = {
    'development': {
        'MODEL_PATH': BASE_DIR / 'core' / 'models',
        'ENABLE_ML': True,
        'FALLBACK_MODE': True,
    },
    'production': {
        'MODEL_PATH': config('MODEL_PATH', default='/app/models'),
        'ENABLE_ML': config('ENABLE_ML', default=True, cast=bool),
        'FALLBACK_MODE': config('ML_FALLBACK_MODE', default=False, cast=bool),
    }
}

# External Service Configuration
EXTERNAL_SERVICES = {
    'SMS_SERVICE': {
        'provider': config('SMS_PROVIDER', default='twilio'),
        'api_key': config('SMS_API_KEY'),
        'api_secret': config('SMS_API_SECRET'),
        'from_number': config('SMS_FROM_NUMBER'),
    },
    'WHATSAPP_SERVICE': {
        'provider': config('WA_PROVIDER', default='twilio'),
        'api_key': config('WA_API_KEY'),
        'api_secret': config('WA_API_SECRET'),
        'webhook_url': config('WA_WEBHOOK_URL'),
    },
    'GOOGLE_MAPS': {
        'api_key': config('GOOGLE_MAPS_API_KEY'),
        'enable_geocoding': config('ENABLE_GEOCODING', default=True, cast=bool),
    }
}

# Feature Flags
FEATURE_FLAGS = {
    'development': {
        'ENABLE_VOICE_INPUT': True,
        'ENABLE_VIDEO_CONSULT': False,
        'ENABLE_AI_DIAGNOSIS': True,
        'ENABLE_EMERGENCY_ALERTS': True,
        'ENABLE_MEDICATION_TRACKING': True,
    },
    'production': {
        'ENABLE_VOICE_INPUT': config('ENABLE_VOICE_INPUT', default=True, cast=bool),
        'ENABLE_VIDEO_CONSULT': config('ENABLE_VIDEO_CONSULT', default=False, cast=bool),
        'ENABLE_AI_DIAGNOSIS': config('ENABLE_AI_DIAGNOSIS', default=True, cast=bool),
        'ENABLE_EMERGENCY_ALERTS': config('ENABLE_EMERGENCY_ALERTS', default=True, cast=bool),
        'ENABLE_MEDICATION_TRACKING': config('ENABLE_MEDICATION_TRACKING', default=True, cast=bool),
    }
}


class Config:
    """Configuration management class"""
    
    def __init__(self, environment=ENVIRONMENT):
        self.environment = environment
    
    def get_database_config(self):
        """Get database configuration for current environment"""
        return DATABASE_CONFIG.get(self.environment, DATABASE_CONFIG['development'])
    
    def get_security_config(self):
        """Get security configuration for current environment"""
        return SECURITY_CONFIG.get(self.environment, SECURITY_CONFIG['development'])
    
    def get_email_config(self):
        """Get email configuration for current environment"""
        return EMAIL_CONFIG.get(self.environment, EMAIL_CONFIG['development'])
    
    def get_logging_config(self):
        """Get logging configuration for current environment"""
        return LOGGING_CONFIG.get(self.environment, LOGGING_CONFIG['development'])
    
    def get_cache_config(self):
        """Get cache configuration for current environment"""
        return CACHE_CONFIG.get(self.environment, CACHE_CONFIG['development'])
    
    def get_api_config(self):
        """Get API configuration for current environment"""
        return API_CONFIG.get(self.environment, API_CONFIG['development'])
    
    def get_ml_config(self):
        """Get ML model configuration for current environment"""
        return ML_CONFIG.get(self.environment, ML_CONFIG['development'])
    
    def get_external_services(self):
        """Get external service configuration"""
        return EXTERNAL_SERVICES
    
    def get_feature_flags(self):
        """Get feature flags for current environment"""
        return FEATURE_FLAGS.get(self.environment, FEATURE_FLAGS['development'])
    
    def is_production(self):
        """Check if running in production"""
        return self.environment == 'production'
    
    def is_development(self):
        """Check if running in development"""
        return self.environment == 'development'


# Global configuration instance
app_config = Config()


def get_config():
    """Get the global configuration instance"""
    return app_config


def update_settings(settings_module):
    """Update Django settings with environment-specific configuration"""
    config = get_config()
    
    # Update database configuration
    db_config = config.get_database_config()
    settings_module.DATABASES['default'].update(db_config)
    
    # Update security settings
    security_config = config.get_security_config()
    settings_module.DEBUG = security_config['DEBUG']
    settings_module.ALLOWED_HOSTS = security_config['ALLOWED_HOSTS']
    settings_module.SECRET_KEY = security_config['SECRET_KEY']
    
    # Add production security settings
    if config.is_production():
        settings_module.SECURE_SSL_REDIRECT = security_config.get('SECURE_SSL_REDIRECT', False)
        settings_module.SECURE_HSTS_SECONDS = security_config.get('SECURE_HSTS_SECONDS', 0)
        settings_module.SECURE_HSTS_INCLUDE_SUBDOMAINS = security_config.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', False)
        settings_module.SECURE_HSTS_PRELOAD = security_config.get('SECURE_HSTS_PRELOAD', False)
    
    # Update email configuration
    email_config = config.get_email_config()
    for key, value in email_config.items():
        setattr(settings_module, key, value)
    
    # Update logging configuration
    settings_module.LOGGING = config.get_logging_config()
    
    # Update cache configuration
    settings_module.CACHES = config.get_cache_config()
    
    # Add CORS settings if available
    api_config = config.get_api_config()
    if 'CORS_ALLOWED_ORIGINS' in api_config:
        settings_module.CORS_ALLOWED_ORIGINS = api_config['CORS_ALLOWED_ORIGINS']
        settings_module.CORS_ALLOW_CREDENTIALS = api_config['CORS_ALLOW_CREDENTIALS']
    
    # Set feature flags in settings
    settings_module.FEATURE_FLAGS = config.get_feature_flags()
    
    # Set external services in settings
    settings_module.EXTERNAL_SERVICES = config.get_external_services()
    
    # Set ML configuration in settings
    settings_module.ML_CONFIG = config.get_ml_config()
