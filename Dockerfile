FROM ubuntu:20.04
RUN apt-get update \
    && apt-get install python3 python3-pip -y \
    && apt-get clean \
    && apt-get autoremove

#  libgl1-mesa-glx libsm6 libxrender1 libxext6

COPY ./requirements.txt /app/requirements.txt
RUN python3 -m pip install -r /app/requirements.txt

ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 -y

RUN apt-get install iputils-ping netcat -y

COPY ./requirements/app.txt /app/requirements.txt
RUN python3 -m pip install -r /app/requirements.txt

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV LANGUAGE=C.UTF-8

EXPOSE 8000
COPY ./ app
WORKDIR /app

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
