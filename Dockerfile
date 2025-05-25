FROM python:3.11-slim

# Set working directory to root
WORKDIR /

# Copy all files from local directory to container root
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask uses
EXPOSE 8000

# Set environment variable for Flask port (Render auto-uses this)
ENV PORT=8000

# Start your bot
CMD ["python", "main.py"]