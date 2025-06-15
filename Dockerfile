FROM python:3.13-slim

# Install necessary system dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    curl \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libfontconfig1 \
    libxcb1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxrender1 \
    libxtst6 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver (versión específica para Chrome 137)
RUN wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/137.0.7151.70/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code
COPY . .

# Configure environment variables for Chrome
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Command to run the worker
CMD ["celery", "-A", "src.tasks", "worker", "--loglevel=info"]
