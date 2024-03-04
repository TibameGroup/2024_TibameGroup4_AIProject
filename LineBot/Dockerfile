FROM python:3.9-slim
COPY  .  /linebot/
WORKDIR  /linebot
RUN  ln -snf /usr/share/zoneinfo/$TZ /etc/localtime\
     && echo $TZ > /etc/timezone\
     && apt-get update\
     && apt-get install -y build-essential\
     && pip install --upgrade pip\
     && apt-get install -y tzdata\  
     && pip install uwsgi\
     && pip install cryptography\ 
     && dpkg-reconfigure -f noninteractive tzdata\
     && pip install -r requirements.txt\
     && apt-get install -y libzbar0     
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0  
ENV FLASK_RUN_PORT=5000 
ENV TZ=Asia/Taipei   
CMD ["sh", "-c","uwsgi -w line:app --http-socket :$PORT --threads 5"]