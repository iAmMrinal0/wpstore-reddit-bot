# WPStore Reddit Bot
A reddit bot for r/windowsphone written in Python to link Windows Phone Store apps when triggered by a keyword.

## Requirements
1. Install [Python 3.4](https://www.python.org/download/releases/3.4.3/)  
2. Install praw, requests, beautifulsoup4, OAuth2Util using separate pip commands or use `pip install -r requirements.txt` to install all required packages in one go.

  - praw - `pip install praw`
  - requests - `pip install requests`
  - beautifulsoup4 - `pip install beautifulsoup4`
  - OAuth2Util - `pip install praw-oauth2util`  

### Reddit Configuration
1. Create a new app on Reddit [here](https://reddit.com/prefs/apps) with `script` type and set `redirect_uri` to `http://127.0.0.1:65010/authorize_callback`  
2. Note the `app key` and `app secret` and paste in `oauth.txt` in respective variables.
3. To post a comment you need the `scope` set to `submit`

## Usage

Run `python wpstorebot.py` and the first time you will be taken to the browser to authenticate your account.  

After authentication, the bot will start to scan new comments which has the keyword `wpapp[]` and any word inside the keyword is taken as the app name to search. After searching for the app links the bot comments with the links.

After commenting, the ID of the parent comment is stored in `comments.txt` so as not to comment again.

## To Do
1. Split the apps for better understanding of similar apps in case of no exact match found.
2. Add logging and infinite run.

### License
 See the [LICENSE](LICENSE) file for license rights and limitations (MIT)
