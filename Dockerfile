FROM python:3.11-slim

# Set working directory to root
WORKDIR /

# Copy all files from local directory to container root
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask uses
EXPOSE $PORT

# Start your bot
CMD ["python", "main.py"]