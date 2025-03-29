#!/bin/sh
USER=docker
HOST=portainer.haakony.no
DIR=/webservers/site-content-balls   # the directory where your website files should go

hugo && rsync -avz --delete public/ ${USER}@${HOST}:~/${DIR} # this will delete everything on the server that's not in the local public folder

exit 0
