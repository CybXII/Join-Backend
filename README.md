# Join-Backend
Backend Applicaton for Join
Testing git-ftp

# Description
This is a backend project developed with Django 5.0.7 and Django REST Framework. It provides an API for managing tasks and projects, including functionalities to create, update, delete, and retrieve tasks and subtasks.

## Technologies
- Django: 5.0.7  
- Django REST Framework: For API development  
- SQLite: Standard database (can be configured)  

## Installation

### Requirements
Make sure you have Python 3.8 or higher and pip installed.

1. Clone the repository:  
   `git clone https://github.com/CybXII/join_angular/tree/main/join_ba`

2. Create and activate a virtual environment with the following commands:  
   `python -m venv env`  
   `source env/bin/activate   # On Windows: env\Scriptsctivate`

3. Install the dependencies:  
   `pip install -r requirements.txt`

4. Configure the database:  
   Run the migrations to initialize the database:  
   `python manage.py migrate`

5. Start the development server:  
   `python manage.py runserver`

## API Endpoints

### Authentication
- `POST /join/signup/`: Register a user  
- `POST /join/login/`: Log in a user  

### Task Management
- `GET /join/tasks/`: Retrieve all tasks  
- `POST /join/tasks/`: Create a new task  
- `PUT /join/tasks/<int:id>/`: Update a specific task  
- `DELETE /join/tasks/<int:id>/`: Delete a specific task  

## Testing
The tests are located in the `join/tests.py` file. To run the tests, use:  
   `python manage.py test`

## Troubleshooting
If you encounter issues, check the following:

- Ensure that the database is correctly configured and migrations have been run.
- Verify the `requirements.txt` for the correct dependency versions.
- If tests fail: Ensure that all necessary data and states are present in the test database.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contributors
Luft Alexander
