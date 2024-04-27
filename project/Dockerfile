FROM python:3.11.6

RUN pip install --upgrade pip

WORKDIR /ESOTERIC-BOT

ADD . /ESOTERIC-BOT

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
