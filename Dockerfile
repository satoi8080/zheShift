FROM python:3.8
# Tried alpine, Faild, C compiler (to install numpy) wasn't found
# Need to install C compiler if alpine is needed in the future
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3", "./app.py"]