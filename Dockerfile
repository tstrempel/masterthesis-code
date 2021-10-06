# syntax=docker/dockerfile:1
# 1. provide base image
FROM fedora:34

# 2. Install tools and Python
RUN dnf install -y \
  git \
  wget \
  python \
  python3 \
  python3-pip \
  zip \
  unzip

# 3. Download and prepare code
RUN git clone https://github.com/tstrempel/masterthesis-code 
WORKDIR masterthesis-code

# 4. Install Python packages based on the bundled requirementes.txt
RUN pip install -r requirements.txt && mkdir /data && chmod u+x reproduction-docker.sh

# 5. Download data
RUN wget https://zenodo.org/record/5550996/files/masterthesis-data.zip

# 6. Set reproduction script as entry point
ENTRYPOINT ["/masterthesis-code/reproduction-docker.sh"] 
