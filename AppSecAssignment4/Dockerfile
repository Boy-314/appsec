from ubuntu:latest

RUN apt-get update && apt-get install -y curl python3 gcc python3-pip
RUN pip3 install --upgrade pip

WORKDIR ./code

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install flask SQLAlchemy

COPY . .

EXPOSE 8080

CMD ["python3", "app.py"]
