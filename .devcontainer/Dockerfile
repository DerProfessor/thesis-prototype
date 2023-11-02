FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Install necessary system dependencies (especially for audio stuff)
RUN apt-get update && \
	apt-get install -y python3-pip python3-venv espeak-ng ffmpeg libportaudio2 \
		libportaudiocpp0 libffmpeg-ocaml libffmpeg-nvenc-dev \
		bash-completion libsndfile1-dev git && \
	apt-get clean

# Create non-root user
RUN useradd -m daniel -u 1000 -s /bin/bash

# Install NodeJS 20
RUN apt-get update && \
	apt-get install -y ca-certificates curl gnupg && \
	mkdir -p /etc/apt/keyrings && \
	curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
	echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
	apt-get update && \
	apt-get install -y nodejs && \
	corepack enable && \
	apt-get clean

# Install coqui-tts
RUN mkdir /Python3_venvs && \
	cd /Python3_venvs && \
	python3 -m venv coqui-tts && \
	. ./coqui-tts/bin/activate && \
	pip3 install 'tts==0.19.1' && \
	rm -rf $HOME/.cache/pip

# Install dependencies for whisper playground
COPY requirements-whisper.txt /Python3_venvs
RUN cd /Python3_venvs && \
	python3 -m venv whisper && . ./whisper/bin/activate && \
	pip3 install -U pip setuptools wheel && \
	pip3 install -r requirements-whisper.txt && \
	rm -rf $HOME/.cache/pip
