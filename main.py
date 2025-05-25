import os
import cohere
import praw
import schedule
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from threading import Thread, Event

load_dotenv()

app = Flask(__name__)
keep_alive_event = Event()

# Configure logging
logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Reddit API Configuration
REDDIT = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    username=os.getenv('REDDIT_USERNAME'),
    password=os.getenv('REDDIT_PASSWORD'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)

COHERE = cohere.Client(os.getenv('COHERE_API_KEY'))

MODIFIERS = [
    "Respond like a genuine Reddit user - use casual language, mild sarcasm, and occasional typos. Keep it conversational with 1-2 short sentences max. Avoid formal structure and AI phrasing."
]

PROCESSED_POSTS_FILE = 'processed_posts.txt'
SUBREDDIT = "AskReddit"
CHECK_INTERVAL = 900  # 15 minutes


def load_processed_posts():
    try:
        with open(PROCESSED_POSTS_FILE, 'r') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def save_processed_post(post_id):
    with open(PROCESSED_POSTS_FILE, 'a') as f:
        f.write(f"{post_id}\n")


def build_prompt(post_title):
    modifier = MODIFIERS[0]  # Directly use the single modifier
    if not post_title.endswith("?"):
        post_title += "?"
    
    prompt = f"Write a Reddit comment responding to this post on r/{SUBREDDIT}. {modifier}:\n\n"
    prompt += f"{post_title}\n\n"

    prompt += f"""
    Follow these rules: 
    - No lists/bullets
    - Maximum 200 tokens (about 40 words)
    - End responses naturally
    - Keep responses SHORT (max 1-3 sentences)
    - Style Guide:
    - Sound like a real human comment, not formal AI
    - Use internet slang occasionally
    - 1-2 sentences max
    - No perfect grammar
    -  Use 80% lowercase letters
    - Use common abbreviations occasionally (lol,fr, smh)
        """


    return prompt


def generate_reply(post_title):
    try:
        prompt = build_prompt(post_title)
        response = COHERE.generate(
            model='command',
            prompt=prompt,
            max_tokens=200,  # Increased buffer
            temperature=0.97,  # Slightly less chaotic
            stop_sequences=["\n\n"],  # Natural conversation stoppers
            frequency_penalty=0.5 
        )
        return response.generations[0].text.strip()
    except Exception as e:
        logging.error(f"Error generating reply: {str(e)}")
        # return "Oops, my sarcasm module malfunctioned. Try again?"
        return None


def check_and_comment():
    processed = load_processed_posts()
    subreddit = REDDIT.subreddit('AskReddit')
    
    try:
        for post in subreddit.new(limit=10):
            if post.id not in processed and not post.locked:
                reply_text = generate_reply(post.title)
                if reply_text:
                    # Post comment
                    post.reply(reply_text)
                    save_processed_post(post.id)
                    logging.info(f"Commented on {post.title} #({post.id}): {reply_text}")
                    print(f"Commented on: {post.title}")
                    print(reply_text)
                    return  # Only comment on one post per check
    except Exception as e:
        logging.error(f"Reddit error: {str(e)}")

def run_scheduler():
    while not keep_alive_event.is_set():
        schedule.run_pending()
        time.sleep(1)

def start_server():
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

def ping_self():
    base_url = os.getenv('LIVE_URL')
    while not keep_alive_event.is_set():
        try:
            requests.get(f"{base_url}/ping")
            logging.info("Keep-alive ping sent")
        except Exception as e:
            logging.error(f"Ping failed: {str(e)}")
        time.sleep(10)

@app.route('/')
def home():
    return "Bot is running", 200

@app.route('/ping')
def ping():
    return "pong", 200

if __name__ == "__main__":
    # Start web server
    server_thread = Thread(target=start_server)
    server_thread.start()

    # Start ping keep-alive
    ping_thread = Thread(target=ping_self)
    ping_thread.start()

    # Start scheduler
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()

    # Initial check
    check_and_comment()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        keep_alive_event.set()
        server_thread.join()
        ping_thread.join()
        scheduler_thread.join()

# def main():
#     logging.info("=== Bot Started ===")
#     # Initial check
#     check_and_comment()
    
#     # Schedule hourly checks
#     schedule.every(59).minutes.do(check_and_comment)
    
#     while True:
#         schedule.run_pending()
#         time.sleep(60)

# if __name__ == "__main__":
#     main()
#     # check_and_comment()

# if __name__ == "__main__":
#     logging.info("Session started")
#     while True:
#         user_input = input("\nAskReddit Question > ")
#         if user_input.lower() in ["exit", "quit"]:
#             logging.info("Session ended")
#             break
        
#         reply = generate_reply(user_input)
#         print(f"\n🤖 Bot's Reply: {reply}")
        
#         # Log both question and response
#         logging.info(f"Question: {user_input}")
#         logging.info(f"Response: {reply}")