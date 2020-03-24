FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN sudo apt-get install gnupg
RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
RUN sudo apt-get update
RUN sudo apt-get install -y mongodb-org
RUN sudo systemctl daemon-reload
RUN sudo systemctl start mongod

COPY . .

CMD [ "python", "run.py"]
