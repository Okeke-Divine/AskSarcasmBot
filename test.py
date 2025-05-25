import os
import cohere
import praw
import schedule
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
print("Environment variables loaded:")
print(f"USERNAME: {os.getenv('REDDIT_USERNAME')}")