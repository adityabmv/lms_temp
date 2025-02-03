# Use the official Python 3.12 image as the base
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Install Poetry globally
RUN pip install poetry

# Copy project files to the container
COPY . .

# Ensure logs directory exists
RUN mkdir -p /app/logs

# Set up Poetry environment variables
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Install project dependencies using Poetry
RUN poetry install --no-root

# Expose port 8000 (Django default)
EXPOSE 8000

ENV FIREBASE_ADMIN_SDK_CREDENTIALS_PATH=/app/credentials/creds.json

CMD ["sh", "-c", "poetry run python manage.py makemigrations && poetry run python manage.py migrate && poetry run python manage.py runserver 0.0.0.0:8000"]

# Command to run the Django development server
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
