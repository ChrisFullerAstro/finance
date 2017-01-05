FROM python:3-onbuild
COPY . /finance
WORKDIR /finance
RUN pip install -r requirements.txt
CMD python app/app.py
