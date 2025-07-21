FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip sumo sumo-tools sumo-doc && \
    apt-get clean

WORKDIR /app

COPY . /app

RUN pip3 install traci requests

ENV SUMO_HOME=/usr/share/sumo
ENV PATH="$SUMO_HOME/bin:$PATH"

CMD ["python3", "entrypoint.py"]
