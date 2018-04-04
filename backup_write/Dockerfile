FROM python:3.7-rc-alpine3.7

RUN apk update
RUN apk add rsync
RUN apk add openssh
RUN ln -s /usr/local/bin/python /bin/python

RUN adduser -D writer && passwd -u writer
COPY howto /etc/motd

COPY hlb.py /bin/hlb
RUN chmod +x /bin/hlb

COPY backup.py /bin/backup
RUN chmod +x /bin/backup

COPY restore.py /bin/restore
RUN chmod +x /bin/restore

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
