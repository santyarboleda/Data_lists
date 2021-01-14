FROM python:3.7

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# install java runtime environment
RUN apt install -y default-jre

RUN mkdir /usr/app

WORKDIR /usr/app

ADD ./ ./

# install crontab
RUN apt-get update && apt-get -y install cron

# copy jobs file to the cron.d directory
COPY jobs /etc/cron.d/jobs

# give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/jobs

# apply cron job
RUN crontab /etc/cron.d/jobs

# create the log file to be able to run tail
RUN touch /var/log/cron.log

# run the command on container startup
CMD cron && tail -f /var/log/cron.log

# install requirements
RUN pip install -r requirements.txt

EXPOSE 3000

CMD ["python", "./app.py"]

