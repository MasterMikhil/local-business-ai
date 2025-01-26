
FROM python

WORKDIR /usr/src/app

COPY . . 

RUN chmod +x /usr/src/app

RUN pip3 install -r requirements.txt

CMD python /usr/src/app/app.py