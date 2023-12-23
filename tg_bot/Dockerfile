FROM python:3.11
RUN mkdir /usr/src/app/
WORKDIR /usr/app/app
COPY tg_bott /usr/src/app
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
