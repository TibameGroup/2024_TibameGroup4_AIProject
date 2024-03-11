FROM ultralytics/ultralytics:8.1.7-python
WORKDIR  /yolo
COPY  .  /yolo/
RUN  apt-get update\
      && apt-get install -y build-essential\
      && pip install --upgrade pip\
     && pip install uwsgi\
     && pip install -r requirements.txt 

CMD ["sh", "-c","uwsgi -w app:app --http-socket :$PORT --threads 5"]