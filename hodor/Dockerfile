FROM python:3.7

RUN useradd demo

WORKDIR /home/demo

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.txt requirements.txt

COPY . .
RUN pip install /home/demo/

ENV FLASK_APP app.py
RUN chown -R demo:demo /home/demo
USER demo

EXPOSE 8000
EXPOSE 8082
CMD ["gunicorn","-w","1","-b","0.0.0.0:8000","app:app","--log-level","debug",\
"--access-logfile","-",\
"--statsd-host=localhost:9125",\
"--worker-class","gevent","--worker-connections","50",\
#"--threads","10",\
"--access-logformat", "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s %(D)s %(f)s %(a)s","--log-syslog"]
