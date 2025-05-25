import os
import cohere
import praw
import schedule
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

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
    "respond exactly like a real human would - use casual language, sarcastic humor, and natural imperfections. " 
    "and relatable analogies. Avoid AI patterns and formal responses."
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
    
    prompt = f"Act as a seasoned Redditor responding to r/{SUBREDDIT} {modifier}:\n\n"
    prompt += f"""
    Follow these rules: 
            1. Maximum 200 tokens (about 40 words)
            2. End responses naturally
            3. Keep responses SHORT (max 1-3 sentences)
            4. Style Guide:
- Sound like a real human comment, not AI
- Use internet slang 
- 1-2 sentences max
            5. Content Rules:
- No perfect grammar
            6. Extra
            - Respond like a sarcastic Reddit veteran using an austrian accent
            -  Use 80% lowercase letters
            - Use common abbreviations (ikr, fr, smh, tl;dr)
        """
    prompt += f"Post Question: {post_title}\n\n"


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
                    logging.info(f"Commented on {post.id}: {reply_text[:50]}...")
                    print(f"Commented on: {post.title}")
                    return  # Only comment on one post per check
    except Exception as e:
        logging.error(f"Reddit error: {str(e)}")

def main():
    logging.info("=== Bot Started ===")
    # Initial check
    check_and_comment()
    
    # Schedule hourly checks
    schedule.every(59).minutes.do(check_and_comment)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # main()
    check_and_comment()

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