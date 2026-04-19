# SwasthyaSaathi Django Project (Enhanced V2)

A comprehensive, connected backend system for rural healthcare with solid architecture and service-oriented design.

## 🏗️ Architecture Overview

This version includes a completely restructured backend with:
- **Service Layer Architecture**: Business logic separated from views
- **Proper Database Models**: Full ORM integration with relationships
- **RESTful API Design**: Versioned endpoints with proper serialization
- **Authentication System**: Token-based auth with user roles
- **Error Handling**: Comprehensive error management and logging
- **Configuration Management**: Environment-based configuration
- **Data Migration**: Automated data loading from CSV/JSON files

## 🚀 Features

### Core Functionality
- **Multilingual Support**: English, Hindi, Gujarati, Marathi, Tamil
- **AI-Powered Symptom Analysis**: ML-based condition prediction
- **Three-Level Triage**: Self-care / Visit clinic / Emergency
- **Nearby Facilities**: Location-based healthcare facility finder
- **Emergency Guides**: Step-by-step first aid instructions
- **ASHA Worker Mode**: Patient management and follow-up
- **Medicine Reminders**: Track doses and adherence

### Technical Features
- **User Management**: Patients, ASHA workers, Admin roles
- **Chat Sessions**: Persistent symptom analysis history
- **Facility Management**: Hospitals, clinics, pharmacies
- **Medicine Database**: Drug information and interactions
- **Audit Logging**: Complete action tracking
- **API Rate Limiting**: Protection against abuse
- **Caching**: Performance optimization

## 📋 System Requirements

- Python 3.8+
- Django 5.1+
- PostgreSQL (Production) / SQLite (Development)
- Redis (Production caching)

## 🛠️ Installation & Setup

### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd swasthya_django_v2

# Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the project root:

```env
# Environment
ENVIRONMENT=development

# Security (Production)
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database (Production)
DB_NAME=swasthya_db
DB_USER=swasthya_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email (Production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# External Services
GOOGLE_MAPS_API_KEY=your-maps-api-key
SMS_PROVIDER=twilio
SMS_API_KEY=your-sms-api-key
SMS_API_SECRET=your-sms-secret
SMS_FROM_NUMBER=your-twilio-number

# Redis (Production)
REDIS_URL=redis://127.0.0.1:6379/1
```

### 4. Database Setup
```bash
# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Load initial data
python migrate_data.py

# Create superuser
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`

## 📡 API Documentation

### Authentication Endpoints

#### Register Patient
```http
POST /api/v2/auth/register/
Content-Type: application/json

{
  "username": "patient123",
  "email": "patient@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "village": "RuralVillage",
  "age": 30,
  "gender": "M",
  "medical_history": ["diabetes"],
  "allergies": ["penicillin"]
}
```

#### Login
```http
POST /api/v2/auth/login/
Content-Type: application/json

{
  "username": "patient123",
  "password": "securepassword"
}
```

### Chat & Symptom Analysis

#### Analyze Symptoms
```http
POST /api/v2/chat/
Authorization: Token your-auth-token
Content-Type: application/json

{
  "message": "I have fever and headache for 2 days",
  "session_id": "optional-existing-session-id"
}
```

### Facilities

#### Get Nearby Facilities
```http
GET /api/v2/facilities/?lat=19.0760&lng=72.8777&type=hospital&radius=10
Authorization: Token your-auth-token
```

#### Get Recommended Facility
```http
GET /api/v2/facilities/recommend/?lat=19.0760&lng=72.8777&urgency=emergency
Authorization: Token your-auth-token
```

### Patients (ASHA Workers)

#### Get Assigned Patients
```http
GET /api/v2/patients/
Authorization: Token your-asha-token
```

#### Add New Patient
```http
POST /api/v2/patients/
Authorization: Token your-asha-token
Content-Type: application/json

{
  "username": "newpatient",
  "email": "new@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1234567890",
  "village": "SameVillage",
  "age": 25,
  "gender": "F"
}
```

### Medicine Management

#### Get Medicines
```http
GET /api/v2/medicines/?search=paracetamol
Authorization: Token your-auth-token
```

#### Get Medicine Reminders
```http
GET /api/v2/medicine-reminders/
Authorization: Token your-patient-token
```

#### Create Medicine Reminder
```http
POST /api/v2/medicine-reminders/
Authorization: Token your-patient-token
Content-Type: application/json

{
  "medicine_id": 1,
  "dosage": "500mg",
  "frequency": "twice daily",
  "next_dose": "2024-01-15T08:00:00Z",
  "notes": "Take with food"
}
```

## 🏛️ Architecture Patterns

### Service Layer
- `ChatService`: Symptom analysis and ML predictions
- `FacilityService`: Healthcare facility management
- `MedicineService`: Medicine and reminder logic
- `UserService`: User and patient management

### Models
- `User`: Extended user with roles (patient/asha/admin)
- `Patient`: Patient profiles with medical history
- `Symptom`: Medical symptoms with severity scores
- `Condition`: Diseases with urgency levels
- `Facility`: Healthcare facilities with location data
- `ChatSession`: Symptom analysis history
- `Medicine`: Drug database
- `MedicineReminder`: Patient medication schedules

### API Versioning
- V1: Legacy endpoints (for compatibility)
- V2: New service-based endpoints

## 🔧 Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Install development dependencies
pip install flake8 black isort

# Format code
black .
isort .

# Lint code
flake8 .
```

### Database Migrations
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

## 🚀 Deployment

### Production Setup
1. Set `ENVIRONMENT=production` in `.env`
2. Configure PostgreSQL database
3. Set up Redis for caching
4. Configure email service
5. Set up SSL certificates
6. Configure reverse proxy (nginx)
7. Set up process manager (gunicorn + supervisor)

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "swasthya_django.wsgi:application"]
```

## 📊 Monitoring & Logging

### Log Levels
- `INFO`: API requests, user actions
- `WARNING`: API errors, security events
- `ERROR`: System errors, exceptions
- `CRITICAL`: Critical failures

### Monitoring Endpoints
- Health check: `/health/`
- Metrics: `/metrics/`
- Status: `/status/`

## 🔒 Security Features

- Token-based authentication
- Role-based access control
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Rate limiting
- Audit logging

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Email: support@swasthyasaathi.org
- Documentation: [Wiki](link-to-wiki)

## 🙏 Acknowledgments

- Original dataset providers for symptom data
- Django REST Framework team
- Scikit-learn for ML capabilities
- Open-source community

---

**Note**: This is a healthcare application. Always consult qualified medical professionals for diagnosis and treatment. This app provides triage assistance and should not replace professional medical advice.
