FROM python:3.7

ARG datapool
WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 80
WORKDIR /app/namenode
CMD ["python", "-u", "namenode.py"]