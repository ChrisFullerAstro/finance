FROM python:3-onbuild
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /finance
WORKDIR /finance
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app/app.py"]
