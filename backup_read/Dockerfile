FROM python:3.7-rc-alpine3.7

RUN apk update
RUN apk add rsync
RUN apk add openssh

COPY howto /etc/motd

COPY ./ssh /etc/ssh
RUN adduser -D reader && passwd -u reader
COPY authorized_keys /home/reader/.ssh/authorized_keys

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
