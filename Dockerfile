FROM ubuntu:18.04

WORKDIR /app/

RUN apt-get update \
    && apt-get install -y \
      python3 \
      python3-pip \
      python3-pyqt5
COPY requirements.txt ./
RUN python3 --version
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apt-get install -y \
    xserver-xorg \
    xinit \
    lxsession \
    desktop-file-utils \
    raspberrypi-ui-mods \
    rpd-icons \
    gtk2-engines-clearlookspix \
    matchbox-keyboard \
    xterm
COPY . .

CMD [ "python3", "./main.py" ]