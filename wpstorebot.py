import praw
import OAuth2Util
import requests
import re
import time
from bs4 import BeautifulSoup


STORE_LINK = "https://www.windowsphone.com/en-us/search"
SUBREDDIT = ""
SLEEP = 60
BOT_BY = """------

^Bot ^by ^[/u/iammrinal0](/user/iammrinal0)"""


def get_url(app_name):

    set_of_links = ""
    ctrl = 0
    heads = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0)"
             " Gecko/20100101 Firefox/36.0"}

    results = requests.get(STORE_LINK, params={"q": app_name},
                           headers=heads)
    soup = BeautifulSoup(results.content, "html.parser")
    for tag in soup.find_all("a", {"data-os": True}):
        if tag["data-os"] == "app":
            if tag.string is not None:
                univ_url = universal_url(tag["href"])
                publisher = get_publisher(univ_url)
                possible = "Possible matches for *{0}*:\n\n".format(app_name)
                if publisher:
                    if app_name.lower() == tag.string.lower():
                        set_of_links += prepare_comment(
                            tag.string, univ_url, publisher)
                        break
                    else:
                        if ctrl == 0:
                            set_of_links += possible
                        set_of_links += prepare_comment(
                            tag.string, univ_url, publisher, True)
                        ctrl += 1
                    if ctrl == 3:
                        break
    if not set_of_links:
        set_of_links = "This app was not found: *{0}*\n\n".format(app_name)
    return set_of_links


def prepare_comment(app_name, app_url, app_dev, possible=None):
    tabs = ""
    if possible:
        tabs = "* "
    return "{0}[{1}]({2}) by {3}\n\n".format(tabs, app_name, app_url, app_dev)


def get_publisher(app_url):
    heads = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0)"
             " Gecko/20100101 Firefox/36.0"}

    results = requests.get(app_url, headers=heads)

    soup = BeautifulSoup(results.content, "html.parser")
    publisher = soup.find("div",
                          {"class": "content m-b-n clamp-5"}
                          )
    if publisher:
        return publisher.text.strip()


def universal_url(url):
    return "{0}s?appid={1}".format(url[:28], url[-36:])


def replied_file(comm_id):
    with open("comments.txt", "a") as f:
        f.write("\n")
        f.write("\n".join(comm_id))


def post_comment(comment, reply, comment_submission):
    if comment_submission:
        comment.reply(reply)
    else:
        comment.add_comment(reply)
    return comment.id


def get_app_name(stri):
    trigger = "\w*wpapp\[([^]]*)\]"
    exp = re.compile(trigger, re.I)
    found = exp.findall(stri)
    if found:
        return found


def bot_process(text, comment_submission, replied_id):
    comment_id = []
    if comment_submission:
        data = text.body
    else:
        data = text.selftext
    trigger_found = get_app_name(data)
    if trigger_found and not str(text.id) in replied_id:
        app_names = []
        for apps in trigger_found:
            if any("," in s for s in apps):
                name = apps.split(",")
                for app_split in name:
                    app_names.append(app_split.strip().lower())
            else:
                app_names.append(apps.strip().lower())

        url = ""
        for name in app_names:
            url += get_url(name)
        if url:
            print("commenting...")
            done_id = post_comment(text, url + BOT_BY, comment_submission)
            comment_id.append(str(done_id))
    return comment_id


def main():

    with open("comments.txt", "r") as f:
        replied_id = f.read().splitlines()

    r = praw.Reddit(user_agent="WP Store Linker v0.1 by /u/iammrinal0")
    OAuth2Util.OAuth2Util(r)

    sub = r.get_subreddit(SUBREDDIT)
    print("Starting Bot...")

    while True:
        sub.refresh()
        comment_id = []
        for comment in sub.get_comments():
            cmnt_id = bot_process(comment, True, replied_id)
            if cmnt_id:
                comment_id.extend(cmnt_id)
        if comment_id:
            print("Writing to file...")
            replied_file(comment_id)
            replied_id.extend(comment_id)
        print("Done! Now sleeping for {0}s".format(SLEEP))
        time.sleep(SLEEP)
        comment_id = []
        for submn in sub.get_new():
            cmnt_id = bot_process(submn, False, replied_id)
            if cmnt_id:
                comment_id.extend(cmnt_id)
        if comment_id:
            print("Writing to file...")
            replied_file(comment_id)
            replied_id.extend(comment_id)
        print("Done! Now sleeping for {0}s".format(SLEEP))
        time.sleep(SLEEP)
    replied_file(comment_id)

if __name__ == "__main__":
    main()
