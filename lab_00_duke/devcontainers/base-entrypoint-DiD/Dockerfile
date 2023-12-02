FROM docker:dind

# Install essential tools and dependencies
RUN apk add --no-cache \
    git \
    curl \
    python3 \
    py3-pip \
    bash \
    openrc \
    sudo \
    docker-cli \
    && rm -rf /var/cache/apk/*

# Create the docker group
RUN addgroup docker

# Add a non-root user and add it to the docker group
RUN adduser -D -h /home/vscode vscode \
    && echo "vscode ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/vscode \
    && addgroup vscode docker

# Entrypoint script to start the Docker daemon
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

USER vscode
WORKDIR /workspace
