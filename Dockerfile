FROM python:3.9.12-buster

# install python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

COPY server.py /app/server.py
COPY index.html /app/index.html
COPY entrypoint.sh /app/entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh"]

