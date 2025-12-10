FROM ubuntu:latest
ARG SSH_SCRIPT_PATH

RUN apt-get update && apt-get install -y sudo openssh-client openssh-server

RUN useradd -m -s /bin/bash appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /home/appuser

COPY ssh/ssh-keys.py /home/appuser/ssh-keys.py
RUN chmod +x /home/appuser/ssh-keys.py
RUN chown appuser:appuser /home/appuser/ssh-keys.py
USER appuser
RUN mkdir -p /home/appuser/keys

CMD ["/bin/bash"]