FROM ubuntu:latest
ARG PASSWORD=pass

RUN apt-get update && apt-get install -y sudo openssh-client openssh-server net-tools iputils-ping

RUN useradd -m -s /bin/bash appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# sshd needs a password for login
RUN echo "appuser:${PASSWORD}" | chpasswd

WORKDIR /home/appuser

USER appuser

#sshd needs some additional configuration
RUN sudo mkdir /var/run/sshd
RUN sudo ssh-keygen -A

RUN mkdir -p /home/appuser/keys

EXPOSE 22

CMD ["sudo", "/usr/sbin/sshd", "-D"]
