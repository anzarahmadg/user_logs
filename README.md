# User Activity Log API

A RESTful API for tracking user activities with state management.

## Features
- Token-based authentication
- Create, read, update, and delete activity logs
- State transitions with validation
- Response caching for improved performance

## Installation

1. Clone the repository:
   git clone https://github.com/anzarahmadg/user_logs.git
   cd project-directory

2. Set up a virtual environment and install dependencies:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
  
3. Run migrations:
     python manage.py migrate
   
5. Start the development server:
     python manage.py runserver

## Testing
Execute tests with:
  python manage.py test user_activity.tests

