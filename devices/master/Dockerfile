FROM python:3

COPY *.py ./
COPY public ./public
COPY locale ./locale

RUN apt install libyajl-dev
RUN mkdir config && pip install pychromecast jsonslicer

CMD [ "python", "./zuulac.py" ]

EXPOSE 8000