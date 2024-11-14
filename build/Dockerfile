FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
RUN apt update

ARG DEBIAN_FRONTEND=noninteractive
RUN apt install python3 python3-pip python3-venv python3-opencv libopencv-dev build-essential -y

COPY . /app

WORKDIR /app
RUN pip3 install -r requirements.txt
RUN pip3 install .

WORKDIR /app/stable-diffusion-task
RUN pip3 install -r requirements_cuda.txt
RUN pip3 install .

WORKDIR /app
