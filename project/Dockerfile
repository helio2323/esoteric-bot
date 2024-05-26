FROM python:3.12.3

RUN pip install --upgrade pip

WORKDIR /ESOTERIC-BOT

ADD . /ESOTERIC-BOT

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
