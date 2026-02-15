FROM ubuntu:latest

RUN userdel -r ubuntu

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sudo \
    git \
    python3-venv 

RUN useradd -m -s /bin/bash developer && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER developer
WORKDIR /home/developer

ENTRYPOINT ["/usr/bin/bash"]