ARG python_ver=3.9
ARG os_ver=alpine

FROM python:${python_ver}-${os_ver}

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install --no-cache-dir --upgrade pip -r requirements.txt

COPY . /app

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["app/main.py"]