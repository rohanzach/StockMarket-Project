FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
	git \
	curl \
	&& rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
	&& apt-get install -y nodejs \
	&& rm -rf /var/lib/apt/lists/*

# Install pip
RUN pip install --upgrade pip

# Expose port
EXPOSE 8000 3000