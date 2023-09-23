FROM python:3.11
RUN mkdir -p /usr/tg_bot/parser
WORKDIR /usr/tg_bot/parser
COPY . /usr/tg_bot/parser
RUN pip install -r requirements.txt
CMD ["python", "parser.py"]
