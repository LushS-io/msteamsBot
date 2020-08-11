FROM ubuntu:18.04 as builder
LABEL maintainer="troykirin.io"

# Create app directory
WORKDIR /root/app

USER root

SHELL ["/bin/bash", "-c"]

# Expose ports
EXPOSE 3980/tcp

RUN apt-get --yes update
RUN apt-get -y install sudo
RUN apt-get install --yes curl

# Bundle app source
COPY . .

# ------------ Setup Python ---------------
# Download Python
RUN apt install -y python3
RUN apt install -y python3-pip

# Pip install requirements
# RUN python setup.py

# Install ngrok

# ngrok authentication envVar

# Define default command. 
# CMD [ "gulp", "ngrok-serve" ]

# --------------------------------------------

# I suppose I can just run ngrok from myside to check ports were properly exposed.

FROM builder as python

# Install wget and then install miniconda as well as init it to .bashrc
RUN apt-get install -y wget
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p $HOME/miniconda 
ENV PATH=~/miniconda/bin:${PATH}
RUN conda init
RUN yes|conda install python=3.8.2

FROM python as debugPoint

# CMD [ "conda", "activate base" ]

RUN echo Hello!
# FROM python as serve
# serve teams web app with gulp and then go to rasa_bot and run model as well; both in the background
# ENTRYPOINT bash launch.sh

# pip install requirements
RUN apt-get install -y vim
RUN pip install -r requirements.txt

# Run python app.py on open
# CMD [ "python", "./app.py" ] 
