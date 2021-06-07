FROM python:3
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
RUN echo $TZ > /etc/timezone
COPY main.py main.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["python","-u", "main.py"]