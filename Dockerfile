FROM python:3.9.2-alpine
RUN pip3 install 'requests==2.31.0' 'python-telegram-bot==21.6' 'python-telegram-bot[job-queue]==21.6'
COPY fuelprices-bot.py .
CMD ["python3", "-u", "fuelprices-bot.py"]
