FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /game_store_epam
COPY requirements.txt /game_store_epam
RUN pip install -r requirements.txt
COPY . /game_store_epam/

#RUN chmod +x /game_store_epam/docker-entrypoint.sh
#
#ENTRYPOINT [ "/game_store_epam/docker-entrypoint.sh" ]