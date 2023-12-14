FROM docker:dind

ENV AID_ENV "dev-did-sudo-v0.0.4"

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


# Copy and set permissions for the start-dockerd.sh script
COPY start-dockerd.sh /workspace/start-dockerd.sh
RUN chmod +x /workspace/start-dockerd.sh

USER vscode
WORKDIR /workspace


