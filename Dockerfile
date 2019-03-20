FROM python:3.6.5
MAINTAINER Karyadi "karyadi@alphatech.id"
RUN mkdir -p /demo
COPY . /demo
RUN pip install -r /demo/requirements.txt
WORKDIR /demo
ENTRYPOINT ["python3"]
CMD ["app.py"]
