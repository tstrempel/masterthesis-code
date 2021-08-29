# syntax=docker/dockerfile:1
# 1. provide base image
FROM fedora:34

# 2. Install tools and Python
RUN dnf install -y \
  git \
  curl \
  jq \
  findutils \
  xz \
  python \
  python3 \
  python3-pip

# 3. Download and prepare code
RUN git clone https://github.com/tstrempel/masterthesis-code
WORKDIR /masterthesis-code

# 4. Install Python packages based on the bundled requirementes.txt
RUN pip install -r requirements.txt
RUN mkdir plots

# 5. Download data
RUN curl https://sandbox.zenodo.org/api/records/887086 | jq '.files[].links.self' | xargs -n 1 curl -O

# 6. Decompress data
RUN for file in *.tar.xz; do tar -Jxf "$file"; done

# 7. Beautify the JSON input data
RUN js-beautify vpxenc-vtune/energy_data.json > vpxenc-vtune/energy_data_beautified.json

#ä 8. Run the Python scripts
RUN python evaluation.py vpxenc-vtune/energy_data_beautified.json plots 1.0 15 4 'vtune' 
