FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
# RUN useradd \
#     --create-home \
#     --uid 10001 \
#     appuser

# # Copy the rest of the application code
# COPY --chown=appuser:appuser . .
COPY . .
# USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
# CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "5000"]