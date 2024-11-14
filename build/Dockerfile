FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
RUN apt update

ARG DEBIAN_FRONTEND=noninteractive
RUN apt install python3 python3-pip python3-venv python3-opencv libopencv-dev build-essential -y

COPY . /app

WORKDIR /app

RUN python3 -m venv venv
RUN . ./venv/bin/activate
RUN pip install -r requirements.txt

WORKDIR /app/stable-diffusion-task
RUN pip install -r requirements_cuda.txt
RUN pip install .

WORKDIR /app
