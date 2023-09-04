# Workflow App (Django)

## Description

The Workflow App is a web-based application built using Django, designed to help manage employee tasks and workflow within an organization. It allows employees to create, view, and update tasks, and managers to oversee and assign tasks.

## Project Structure

The project follows a typical Django project structure:

- `core/`: Django project settings and configuration.
- `workflow_app/`: Django app for managing employee-related functionality.
- `home/`: Django app for the home or landing page.
- `static/`: Static files (CSS, JavaScript, Images).
- `staticfiles/`: Static files for production (collected using `collectstatic`).
- `templates/`: HTML templates.
- `venv/`: Virtual environment for Python dependencies.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Abhimanue-rajesh/workflow.V.0.1.git

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
      venv\Scripts\activate # On Mac, use: source venv/bin/activate

3. Install project dependencies:

    ```bash
    pip install -r requirements.txt

4. Apply database migrations:

    ```bash
    python manage.py migrate

5. Create a superuser for the admin panel:

    ```bash
    python manage.py createsuperuser

6. Start the development server:

    ```bash
    python manage.py runserver

7. Access the application in your web browser at http://http://127.0.0.1:8000/
    Usage
        Visit the home page to get started.
        Employees can log in, view tasks, and update their profiles.
        Managers can add, assign, and update tasks.
    Use the admin panel at http://http://127.0.0.1:8000/admin/ to manage users and tasks.





