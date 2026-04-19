# SwasthyaSaathi 🩺
### AI-Powered Healthcare Assistance & Symptom Support Platform

SwasthyaSaathi is a full-stack healthcare web platform designed to provide a simple, accessible, and scalable digital health support experience. It is built with a separate **backend** and **frontend** architecture and includes **Docker** and **Kubernetes** support for modern deployment workflows.

The project is structured like a real-world software product, making it suitable for **academic submission, portfolio showcase, GitHub presentation, and deployment practice**.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Core Modules](#core-modules)
- [How It Works](#how-it-works)
- [Backend](#backend)
- [Frontend](#frontend)
- [Docker Setup](#docker-setup)
- [Kubernetes Setup](#kubernetes-setup)
- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Local Development](#local-development)
- [Running with Docker Compose](#running-with-docker-compose)
- [Kubernetes Deployment](#kubernetes-deployment)
- [API Overview](#api-overview)
- [Use Cases](#use-cases)
- [Future Enhancements](#future-enhancements)
- [Project Highlights](#project-highlights)
- [Challenges Addressed](#challenges-addressed)
- [Learning Outcomes](#learning-outcomes)
- [GitHub Upload Guide](#github-upload-guide)
- [Author](#author)
- [License](#license)

---

## Overview

SwasthyaSaathi is a healthcare-oriented web application built to support users through a structured digital interface for symptom-based interaction and healthcare guidance workflows.

The project follows a modular full-stack architecture:

- **Frontend** handles the user interface and user interaction
- **Backend** handles routes, processing, logic, and APIs
- **Docker** provides a containerized setup for consistent local and production environments
- **Kubernetes** adds scalable deployment support through orchestration manifests

This project is designed not only as an application, but also as a complete engineering project with clean structure, deployment readiness, and professional documentation.

---

## Problem Statement

In many cases, users do not have quick access to basic digital healthcare guidance. Common challenges include:

- difficulty understanding whether symptoms are mild, moderate, or urgent
- lack of accessible healthcare-oriented web tools
- limited availability of organized healthcare support systems
- poor separation of frontend and backend in many student projects
- lack of deployment-ready structure in academic projects

There is a need for a clean, user-friendly, and structured platform that can serve as a digital healthcare assistance solution while also demonstrating proper software engineering practices.

---

## Solution

SwasthyaSaathi addresses this by providing a full-stack healthcare platform with:

- a simple and structured user interface
- symptom-support interaction flow
- healthcare guidance related modules
- clean separation of backend and frontend
- Docker-based containerization
- Kubernetes deployment manifests
- GitHub-ready repository organization

This makes the project both functionally meaningful and technically strong.

---

## Key Features

### Functional Features

- Healthcare assistance platform structure
- Symptom-support interaction workflow
- User-friendly interface for healthcare-related navigation
- Referral-style and guidance-oriented module support
- Admin-side support pages
- Login and signup support structure
- Modular project design for future feature expansion

### Engineering Features

- Separate `backend` and `frontend` directories
- Dockerized setup for backend and frontend
- Docker Compose configuration for local multi-service execution
- Kubernetes manifests for deployment orchestration
- Environment-based configuration support
- GitHub-ready clean folder structure
- Scalable and maintainable project organization

---

## System Architecture

The platform follows a layered full-stack architecture:

```text
User
  ↓
Frontend Interface
  ↓
Backend API / Business Logic
  ↓
Internal Processing / Data Layer / Services
Architecture Breakdown
1. Presentation Layer

The frontend serves as the visual and interactive layer where users interact with the platform.

2. Application Layer

The backend processes requests, manages logic, handles routes, and prepares responses.

3. Deployment Layer

Docker and Kubernetes configurations make the application easier to deploy, scale, and manage.

This separation improves maintainability, deployment flexibility, and future scalability.

Technology Stack
Backend
Python
Django
Gunicorn
WhiteNoise
Frontend
HTML
CSS
JavaScript
Nginx
DevOps / Deployment
Docker
Docker Compose
Kubernetes
Git
GitHub
Configuration / Documentation
Environment variables
YAML
Markdown
Project Structure
SwasthyaSaathi/
│
├── backend/                        # Django backend application
│   ├── core/                       # Main backend app logic
│   ├── swasthya_django/            # Django project configuration
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── other backend files
│
├── frontend/                       # Frontend application / UI structure
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── frontend files
│
├── k8s/                            # Kubernetes manifests
│   ├── namespace.yaml
│   ├── backend-configmap.yaml
│   ├── backend-secret.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   └── ingress.yaml
│
├── docker-compose.yml              # Multi-container local setup
├── .env.example                    # Sample environment variables
├── .gitignore
└── README.md
Core Modules
Landing Module

Acts as the main entry point of the platform and introduces users to the application.

Authentication Module

Supports login and signup-related application structure.

Symptom Interaction Module

Handles user interaction for healthcare and symptom-related flows.

Referral / Guidance Module

Supports healthcare-related guidance and directional workflow modules.

Admin Module

Provides administrative interface support for system handling and monitoring.

Deployment Module

Includes Docker and Kubernetes configuration files for containerized and orchestrated deployment.

How It Works

The overall workflow is simple and modular:

The user opens the web application.
The frontend presents healthcare-related pages and user interaction options.
The user enters data or interacts with a module.
The frontend sends requests to the backend.
The backend processes the request using server-side logic.
A response is generated and returned.
The frontend displays the result to the user.

This client-server communication structure keeps the project clean and scalable.

Backend

The backend is responsible for the server-side logic of the application.

Responsibilities
request handling
business logic processing
route management
API support
data validation
admin-side configuration
deployment integration
Important Backend Files
manage.py

Used for Django management commands such as running the development server and migrations.

models.py

Defines the application's data models.

views.py

Contains the request handling and backend logic.

urls.py

Maps routes to backend views.

admin.py

Configures backend models for admin panel usage.

apps.py

Contains Django app configuration.

serializers.py

Supports structured API input/output formatting.

utils.py

Contains helper functions and reusable logic.

Backend Goals
maintainable logic structure
clear API integration path
deployment-friendly organization
future feature expansion support
Frontend

The frontend is the user-facing layer of the project.

Responsibilities
displaying pages and UI components
handling user interactions
sending requests to backend
rendering returned data
providing a simple healthcare-oriented interface
Frontend Goals
user-friendly interface
clean navigation
independent deployment capability
modular separation from backend
easy future enhancement
Frontend Deployment

The frontend is structured so it can be containerized and served independently through Nginx in a production-style environment.

Docker Setup

Docker support is included to standardize project execution across machines.

Why Docker
avoids dependency mismatch issues
improves portability
supports clean environment setup
simplifies local development and deployment
makes the project more professional
Docker Components
Backend Container

Builds and runs the Django backend.

Frontend Container

Builds and serves the frontend application.

Docker Compose

Runs both services together from a single command.

Kubernetes Setup

Kubernetes support is included to demonstrate scalable deployment architecture.

Why Kubernetes
supports replica-based deployment
separates frontend and backend into services
improves deployment professionalism
reflects real-world production architecture
allows future scaling and orchestration
Kubernetes Manifests Included
namespace.yaml
backend-configmap.yaml
backend-secret.yaml
backend-deployment.yaml
backend-service.yaml
frontend-deployment.yaml
frontend-service.yaml
ingress.yaml
Environment Variables

The project uses environment variables for flexible configuration.

Example
DJANGO_SECRET_KEY=replace-this-with-a-secure-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend,backend-service
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://localhost
Why Environment Variables Matter
prevent hardcoding sensitive values
support multiple environments
improve security and maintainability
simplify deployment configuration
Installation
Prerequisites

Install the following before running the project:

Python 3.x
pip
Git
Node.js and npm
Docker Desktop
Kubernetes tools if using cluster deployment:
kubectl
Minikube or Docker Desktop Kubernetes
Local Development
Backend Setup
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

Backend will typically run on:

http://127.0.0.1:8000
Frontend Setup
cd frontend
npm install
npm run dev

Frontend will typically run on:

http://localhost:5173
Running with Docker Compose

From the project root:

docker-compose up --build

This starts all configured services together.

Benefits
single command startup
backend and frontend run together
easier demo and testing workflow
consistent environment across systems
Kubernetes Deployment

Update image names inside the Kubernetes deployment files, then apply:

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend-configmap.yaml
kubectl apply -f k8s/backend-secret.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/ingress.yaml
Verify
kubectl get pods
kubectl get services
API Overview

The backend is designed to support frontend-backend communication using API-style request handling.

API Responsibilities
accept frontend requests
validate input
process business logic
return structured responses
support modular feature expansion
Example Endpoint Categories
symptom-related endpoints
user-related endpoints
admin-related endpoints
referral / support endpoints
status / health endpoints
Use Cases
1. Healthcare Interaction

A user visits the platform and interacts with healthcare-related modules.

2. Symptom Support

A user enters symptom-related information and receives a structured system response.

3. Referral Guidance

A user explores healthcare guidance or referral-oriented support modules.

4. Admin Management

An admin uses backend management or dashboard pages for platform control.

5. Deployment Demonstration

A developer deploys the application using Docker or Kubernetes.

6. Academic / Portfolio Showcase

A student presents the project as a complete full-stack and deployment-ready system.

Future Enhancements

The platform can be extended further with:

AI-based symptom analysis
multilingual support
voice-based input
nearby hospital and pharmacy lookup
medicine recommendation system
appointment booking
patient profile management
analytics dashboard
secure role-based authentication
cloud deployment pipeline
monitoring and logging integration
Project Highlights
Full-stack healthcare project
Separate backend and frontend architecture
Dockerized deployment support
Kubernetes-ready manifests
GitHub-friendly professional structure
Easy to present, maintain, and scale
Suitable for academic and portfolio use
Challenges Addressed

This project addresses several practical software engineering challenges:

structuring a clean full-stack repository
separating backend and frontend properly
organizing deployment configuration
making a project GitHub-ready
supporting both development and deployment workflows
designing for future scalability
Learning Outcomes

Working on this project demonstrates knowledge in:

full-stack development
Django backend organization
frontend-backend integration
Git and GitHub workflow
Docker containerization
Docker Compose orchestration
Kubernetes basics
project documentation
scalable architecture planning
GitHub Upload Guide
Using Git Terminal
git init
git add .
git commit -m "initial project upload"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main

If remote already exists:

git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main --force
Using GitHub Desktop
Open GitHub Desktop
Add an existing repository from local drive
Select the project folder
Commit the files
Publish the repository

SwasthyaSaathi was prepared as a healthcare-focused full-stack software project with modern deployment support and professional repository organization.

License

This project is intended for educational, academic, and portfolio use.

You may add an MIT License or another open-source license if you want to make the repository publicly reusable.

Final Note

SwasthyaSaathi is more than a basic web project. It is a structured software engineering project that combines:

healthcare-focused application development
full-stack architecture
deployment readiness
clean documentation
GitHub presentation quality

It is suitable for:

academic submission
portfolio presentation
deployment practice
DevOps learning
full-stack project demonstration

## 👥 Contributors

This project was developed by:

*   Falak Shah
*   Hiranshee Doshi
*   Jyotier Vithlani
*   Tanmay Kanani
