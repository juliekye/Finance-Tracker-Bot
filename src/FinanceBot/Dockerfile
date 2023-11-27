# Use the official Python 3.11 image as the base image
FROM python:3.11.4-alpine3.18

# Install required packages
RUN apk add --no-cache nano bash

# Set the working directory
WORKDIR /workspace

# Copy the requirements.txt file into the container
COPY src/FinanceBot/requirements.txt /requirements.txt

# Install the Python packages from requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the necessary files from your local directory to the container
COPY src/FinanceBot/ /workspace/src

# Remove unneeded files
RUN rm /requirements.txt /workspace/src/Dockerfile /workspace/src/requirements.txt

# Create a user
COPY ./src/scripts/create_user.sh /create_user.sh
RUN chmod +x /create_user.sh && /create_user.sh

USER app

# Run the script to start the bot
CMD python3 /workspace/src/start_finance_bot.py
