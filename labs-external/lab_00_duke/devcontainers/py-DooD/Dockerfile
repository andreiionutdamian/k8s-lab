FROM mcr.microsoft.com/devcontainers/python:0-3.11
WORKDIR /workspace

# Install Git and other essential tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Add user to the docker group
# RUN groupadd docker  # usually already exists
RUN usermod -aG docker vscode

ENV AID_ENV "dev-py-dood"

#COPY requirements.txt .
#RUN pip install -r requirements.txt