# AskSarcasmBot

A Reddit bot that replies to new AskReddit posts with responses that sound 100% human — sarcastic, casual, and imperfect.
Powered by Cohere’s language model and PRAW for Reddit interaction.


## What is this?

I built this as an experiment to see if a bot can talk like a real Reddit user
It reads fresh posts from r/AskReddit, crafts replies with sarcastic humor, slang, and natural mistakes, then posts them.


## How it works

* Uses Reddit API (via PRAW) to monitor new AskReddit posts.
* Uses Cohere’s `command` model to generate replies based on a crafted prompt with explicit instructions for human style, slang, and sarcasm.
* Replies only once per post and keeps track so it doesn't spam.
* Logs everything locally for transparency.
* Runs on a schedule — checks every \~hour for new posts.


## Setup and usage

1. Clone repo

2. Create a `.env` file with your secrets:

   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USERNAME=your_reddit_username
   REDDIT_PASSWORD=your_reddit_password
   REDDIT_USER_AGENT=your_user_agent
   COHERE_API_KEY=your_cohere_api_key
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run bot:

   ```bash
   python main.py
   ```


## Important notes

* This is a personal experiment. Use at your own risk.
* The bot isn’t responsible for what it says. It’s AI-generated sarcasm.
* Reddit has strict rules — don’t spam or abuse the API, or you risk bans.
* Keep your credentials safe and never share your `.env`.
* The bot’s output is intentionally imperfect


## Dependencies

* Python 3.8+
* [cohere](https://pypi.org/project/cohere/)
* [praw](https://pypi.org/project/praw/)
* [schedule](https://pypi.org/project/schedule/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)


## License

For education and experimentation only. No warranties. Not liable for any damage or bans resulting from usage.
