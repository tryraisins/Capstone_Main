import os

import logging
import sys
from dotenv import load_dotenv
from logtail import LogtailHandler


load_dotenv(dotenv_path='app/.env')

token = os.getenv("BETTER_STACK_TOKEN")

# Get logger

custom_logger = logging.getLogger()

# Create a formatter

formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s"
)

# Create handlers
stream_handler = logging.StreamHandler(sys.stdout)
better_stack_handler = LogtailHandler(source_token=token)

# Set formatters
stream_handler.setFormatter(formatter)

# Add handlers to the logger
custom_logger.handlers = [stream_handler, better_stack_handler]

# Set log level
custom_logger.setLevel(logging.INFO)