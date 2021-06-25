FROM gorialis/discord.py:minimal

WORKDIR /

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "bot.py"]