FROM ubuntu:latest
ARG PASSWORD=pass

RUN apt-get update && apt-get install -y sudo openssh-client openssh-server python3-venv

RUN useradd -m -s /bin/bash appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# sshd needs a password for login
RUN echo "appuser:${PASSWORD}" | chpasswd

WORKDIR /home/appuser

USER appuser

#sshd needs some additional configuration
RUN sudo mkdir /var/run/sshd
RUN sudo ssh-keygen -A

RUN mkdir -p /home/appuser/.ssh

EXPOSE 22
ADD requirements.txt /home/appuser/requirements.txt
RUN python3 -m venv ssh-venv
RUN /bin/bash -c "source ssh-venv/bin/activate && pip install -r /home/appuser/requirements.txt"

CMD ["sudo", "/usr/sbin/sshd", "-D"]
