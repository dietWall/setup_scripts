FROM ubuntu:latest
ARG SSH_SCRIPT_PATH

RUN apt-get update && apt-get install -y sudo openssh-client openssh-server net-tools

#sshd needs some additional configuration

RUN useradd -m -s /bin/bash appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /home/appuser

USER appuser

RUN sudo mkdir /var/run/sshd
RUN sudo ssh-keygen -A

RUN mkdir -p /home/appuser/keys

EXPOSE 22

CMD ["sudo", "/usr/sbin/sshd", "-D"]
