FROM python:3-onbuild
COPY . /finance
WORKDIR /finance
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app/app.py"]
