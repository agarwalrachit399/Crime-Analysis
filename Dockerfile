FROM python:3.11

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requiremnts.txt

EXPOSE 8080

CMD python app.py