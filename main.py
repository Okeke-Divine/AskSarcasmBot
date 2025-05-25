import os
import cohere
import praw
import schedule
import time
import logging
import requests
import threading
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
import logging

load_dotenv()

app = Flask(__name__)

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
    modifier = MODIFIERS[0]
    if not post_title.endswith("?"):
        post_title += "?"
    
    prompt = f"Write a Reddit comment responding to this post on r/{SUBREDDIT}. {modifier}:\n\n"
    prompt += f"{post_title}\n\n"
    prompt += """
    Follow these rules: 
    - No lists/bullets
    - Maximum 200 tokens (about 40 words)
    - End responses naturally
    - Keep responses SHORT (max 1-3 sentences)
    - Style Guide:
      - Sound like a real human comment, not formal AI
      - Use internet slang occasionally
      - No perfect grammar
      - Use 80% lowercase letters
      - Use common abbreviations occasionally (lol, fr, smh)
    """
    return prompt


def generate_reply(post_title):
    try:
        prompt = build_prompt(post_title)
        response = COHERE.generate(
            model='command',
            prompt=prompt,
            max_tokens=300,
            temperature=0.97,
            stop_sequences=["\n\n"],
            frequency_penalty=0.5 
        )
        return response.generations[0].text.strip()
    except Exception as e:
        logging.error(f"Error generating reply: {str(e)}")
        return None


def check_and_comment():
    print(">>> check_and_comment")
    processed = load_processed_posts()
    subreddit = REDDIT.subreddit(SUBREDDIT)
    
    try:
        for post in subreddit.new(limit=10):
            if post.id not in processed and not post.locked:
                reply_text = generate_reply(post.title)
                if reply_text:
                    post.reply(reply_text)
                    save_processed_post(post.id)
                    logging.info(f"Commented on {post.title} #({post.id}): {reply_text}")
                    print(f"✅ Commented on: {post.title}")
                    print(f"💬 {reply_text}\n")
                    return
    except Exception as e:
        print(f"Reddit error: {str(e)}")


def schedule_loop():
    print(">>> [initial] check_and_comment")
    check_and_comment()

    schedule.every(59).minutes.do(check_and_comment)
    while True:
        schedule.run_pending()
        time.sleep(60)


def ping_loop():
    base_url = os.getenv('LIVE_URL')
    if not base_url:
        print("⚠️ LIVE_URL not set in .env, skipping ping loop.")
        return

    while True:
        try:
            response = requests.get(f"{base_url}/ping")
            print(f"Pinged self")
        except Exception as e:
            print(f"Ping failed: {str(e)}")
        time.sleep(10)


@app.route('/')
def home():
    return "Bot is running", 200

@app.route('/ping')
def ping():
    print(">>> server pinged")
    return "pong", 200


if __name__ == "__main__":
    print("=== Bot Started ===")

    # Start scheduled comment loop
    threading.Thread(target=schedule_loop, daemon=True).start()

    # Start ping loop
    threading.Thread(target=ping_loop, daemon=True).start()

    # Run Flask app
    port = int(os.environ.get('PORT', 8000))
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=port, debug=False)
