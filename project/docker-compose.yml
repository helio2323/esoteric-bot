version: '3.8'

services:
  esoteric-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: esoteric-bot
    ports:
      - "2500:2500"  # ajuste a porta conforme necessário
    command: python3 main.py
    tty: true
