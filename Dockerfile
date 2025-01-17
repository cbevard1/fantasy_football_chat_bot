FROM python:latest

ENV LEAGUE_YEAR=2021
ENV LEAGUE_ID=0
ENV GUILD_ID=0
ENV CHANNEL_ID=0
ENV TOKEN=0
ENV TZ=US/Eastern
ENV TEAM1_DISCORD_ID=0
ENV TEAM2_DISCORD_ID=0
ENV TEAM3_DISCORD_ID=0
ENV TEAM4_DISCORD_ID=0
ENV TEAM5_DISCORD_ID=0
ENV TEAM6_DISCORD_ID=0
ENV TEAM7_DISCORD_ID=0
ENV TEAM8_DISCORD_ID=0
ENV TEAM9_DISCORD_ID=0
ENV TEAM10_DISCORD_ID=0
ENV TEAM11_DISCORD_ID=0
ENV TEAM12_DISCORD_ID=0


# Install app
ADD . /usr/src/ff_bot
WORKDIR /usr/src/ff_bot
RUN python3 setup.py install

# Launch app
CMD ["python3", "ff_bot/ff_bot.py"]