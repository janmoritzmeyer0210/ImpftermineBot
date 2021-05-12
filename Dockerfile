FROM python:3

RUN pip install requirements.txt
CMD ["python", "main.py"]