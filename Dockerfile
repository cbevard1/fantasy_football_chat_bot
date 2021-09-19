FROM python:latest

ENV LEAGUE_YEAR=2021
ENV LEAGUE_ID=0
ENV GUILD_ID=0
ENV CHANNEL_ID=0
ENV TOKEN=0

# Install app
ADD . /usr/src/ff_bot
WORKDIR /usr/src/ff_bot
RUN python3 setup.py install

# Launch app
CMD ["python3", "ff_bot/ff_bot.py"]