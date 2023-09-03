# Build the release image.
FROM ubuntu:latest
LABEL MAINTAINER Jup`s <jupsoops@gmail.com>
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN apt-get update
RUN apt install vim -y
RUN apt install net-tools -y
# RUN apt install iputils-ping -y
RUN apt-get install wget -y
RUN apt-get install unzip -y

#크론탭 설치
RUN apt install cron -y

#파이썬 설치
RUN apt install python3 -y
RUN apt install python3-pip -y

#크롬설치 [크롤링]
ENV CHROME_VERSION=114.0.5735.90
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN wget https://deb.adamhlavacek.com/google-chrome-stable-${CHROME_VERSION}-1_amd64.deb
RUN apt install ./google-chrome-stable-${CHROME_VERSION}-1_amd64.deb -y
RUN rm -rf ./google-chrome-stable-${CHROME_VERSION}-1_amd64.deb

#크롬드라이버 설치 [크롤링]
RUN wget -N https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN rm -rf ./chromedriver_linux64.zip
RUN mv ./chromedriver /usr/bin/chromedriver

#파이썬 모듈설치
RUN python3 -m pip install --upgrade pip
RUN pip install selenium
RUN pip install BeautifulSoup4
RUN pip install cachetools
#웹프레임워크
RUN pip install flask
#파이썬 코드로 크론탭 등록
RUN pip install python-crontab
#mysql
#RUN pip install SQLAlchemy 
RUN pip install mysql-connector-python
#csrf protect
RUN pip install flask-WTF
#login
RUN pip install flask-login
RUN pip install Flask-Bcrypt
RUN pip install email-validator

#timezone Asia/Seoul
ENV TZ=Asia/Seoul
RUN apt install tzdata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Locale
RUN apt-get install -y locales git
RUN localedef -f UTF-8 -i ko_KR ko_KR.UTF-8
ENV LC_ALL ko_KR.UTF-8
ENV PYTHONIOENCODING=utf-8

RUN mkdir -p /usr/src/app && cd /usr/src/app 

WORKDIR /usr/src/app

# VOLUME . /usr/src/app

EXPOSE 8800


#도커 빌드하고 실행하기
#docker build -t ubuntu .

#(linux remote)
#docker run -it -p 8800:8800 -v /home/ubuntu/test/:/usr/src/app --name test ubuntu 


#(window local)
#docker run -it -p 8800:8800 -v D:\Documents\jups_project\smartstore:/usr/src/app --name store ubuntu 

# crontab -e
#파이썬 주기 작업 스마트스토어 배송건수 입력 (매주 월요일 22시에 실행)
#0 22 * * 1 /usr/bin/python3 /usr/src/app/cron_process_weekly.py >> /usr/src/app/logs/cron.log
#파이썬 주기 작업 스마트스토어 배송건수 입력 테스트 (매일 0시 5분에)
#5 0 * * * /usr/bin/python3 /usr/src/app/cron_process_daily.py >> /usr/src/app/logs/cron.log

#service cron restart