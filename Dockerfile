# Use the official Python image
FROM python:3.12

# Set working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# # Expose the port that Flask runs on
# EXPOSE 5000

# # Define environment variables for MongoDB connection
# ENV MONGO_HOST=mongo
# ENV MONGO_PORT=27017

# # Define environment variables
# ENV FLASK_APP=app.py
# ENV FLASK_RUN_HOST=0.0.0.0
# ENV FLASK_ENV=development

# ENV PYTHONUNBUFFERED=1  

# # Start the Flask application
CMD ["python", "app.py"]