# syntax=docker/dockerfile:1
FROM fedora:34

RUN dnf install -y \
  git \
  curl \
  jq \
  findutils \
  xz \
  python \
  python3 \
  python3-pip
RUN git clone https://github.com/tstrempel/masterthesis-code
WORKDIR /masterthesis-code
RUN pip install -r requirements.txt
RUN mkdir plots
RUN curl https://sandbox.zenodo.org/api/records/887086 | jq '.files[].links.self' | xargs -n 1 curl -O
RUN for file in *.tar.xz; do tar -Jxf "$file"; done
RUN js-beautify vpxenc-vtune/energy_data.json > vpxenc-vtune/energy_data_beautified.json
RUN python evaluation.py vpxenc-vtune/energy_data_beautified.json plots 1.0 15 4 'vtune' 
