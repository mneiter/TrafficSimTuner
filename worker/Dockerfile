FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip sumo sumo-tools sumo-doc && \
    apt-get clean

# Set working directory inside container
WORKDIR /app

# Copy project files into container
COPY . /app

# Install Python dependencies
RUN pip3 install traci requests

# Set SUMO environment
ENV SUMO_HOME=/usr/share/sumo
ENV PATH="$SUMO_HOME/bin:$PATH"

# Run entrypoint on container start
CMD ["python3", "entrypoint.py"]
