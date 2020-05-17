FROM python:3

COPY *.py ./
COPY public ./public
COPY locale ./locale

RUN mkdir config && pip install qrcode[pil] python-telegram-bot ecdsa

CMD [ "python", "./zuulac.py" ]

EXPOSE 8000