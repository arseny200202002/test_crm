FROM python:3.12-alpine


WORKDIR /usr/src/crm
RUN pip install --upgrade pip
COPY requirements.txt /usr/src/crm/

RUN pip install -r requirements.txt
COPY . /usr/src/crm/

RUN python manage.py collectstatic --noinput
RUN python manage.py createsuperuser --noinput

EXPOSE 8080

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]