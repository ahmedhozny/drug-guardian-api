# Drug Guardian Pro

Drug Guardian Pro is a robust API designed to provide drug synergy prediction and side effects analysis. It offers endpoints for health checks, user authentication, file uploads, and drug interaction predictions, all built on the FastAPI framework. The API also includes advanced features such as logging, monitoring, and caching for enhanced performance and reliability.

## Features

- **API Gateway**: Centralized entry point for all API requests, managing routing, rate limiting, and security.
- **HTTP Server**: Built on FastAPI, offering high performance and easy scalability.
- **Database and Caching Layer**: Utilizes MySQL for persistent storage and a caching mechanism for improved performance.
- **Authentication & Authorization**: Implements JWT and OAuth2 for secure authentication and authorization, with support for Kerberos for enterprise-level security.
- **Logging**: Comprehensive logging using Logtail (BetterStack) for real-time log management and analysis.
- **Machine Learning Model Layer**: Scalable model instances for drug synergy and side effects prediction.

## Installation

### Prerequisites

- Python 3.7+
- Docker (optional, for containerized deployment)
- MySQL
- Redis
- Kerberos (Optional)

### Clone the Repository

```bash
git clone https://github.com/ahmedhozny/drugGuardian-pro.git
cd drug-guardian-pro
```

### Environment Variables
Example env file ".env.example":
```
DB_USER=root
DB_PASSWD=password123
DB_NAME=DrugGuardian
DB_SERVER="127.0.0.1"
DB_TEST=FALSE
TOKEN_UVICORN="{TOKEN}"
TOKEN_REQUESTS="{TOKEN}"

MAIL_USERNAME=abcd@ethereal.email
MAIL_PASSWORD=QWWcq9A69KhGCnrfj3
MAIL_FROM=abcd@ethereal.email
MAIL_PORT=587
MAIL_SERVER=smtp.ethereal.email
MAIL_FROM_NAME="Drug Guardian"
```

### Install Dependencies
```
pip install -r requirements.txt
```

### Run the Application
```
uvicorn main:app --reload
```


### Logging
Logging is configured using Python's logging module and Logtail (BetterStack) for structured log management.

- Request Logs: Stored in requests.log and sent to Logtail.
- Application Logs: Stored in uvicorn.log and sent to Logtail.
