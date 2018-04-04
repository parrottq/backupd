FROM python:3.7-rc-alpine3.7

RUN apk update
RUN apk add rsync
RUN apk add openssh

RUN adduser -D reader && passwd -u reader

COPY howto /etc/motd

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
