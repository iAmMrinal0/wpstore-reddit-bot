import praw
import OAuth2Util
import requests
import re
from bs4 import BeautifulSoup


STORE_LINK = "https://www.windowsphone.com/en-us/search"
SUBREDDIT = ""
REPLIED_COMMENTS = []
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
                if tag.string.lower() == app_name.lower():
                    set_of_links += "[{0}]({1})\n\n".format(
                        tag.string, tag["href"])
                    break
                elif app_name.lower() in tag.string.lower():
                    set_of_links += "[{0}]({1})\n\n".format(
                        tag.string, tag["href"])
                    ctrl += 1
                    if ctrl == 3:
                        break
                else:
                    set_of_links += "[{0}]({1})\n\n".format(
                        tag.string, tag["href"])
                    ctrl += 1
                    if ctrl == 3:
                        break

    return set_of_links


def replied_file(comm_id):
    with open("comments.txt", "a") as f:
        f.write("\n")
        f.write("\n".join(comm_id))


def post_comment(comment, reply):
    comment.reply(reply)
    return comment.id


def get_app_name(stri):
    trigger = "\w*wpapp\[([^]]*)\]"
    exp = re.compile(trigger)
    found = exp.findall(stri)
    if found:
        return found


def main():

    comment_id = []
    with open("comments.txt", "r") as f:
        REPLIED_COMMENTS = f.read().splitlines()

    r = praw.Reddit(user_agent="WP Store Linker v0.1 by /u/iammrinal0")
    o = OAuth2Util.OAuth2Util(r)
    o.refresh()

    sub = r.get_subreddit(SUBREDDIT)
    comments = sub.get_comments()

    for comment in comments:
        trigger_found = get_app_name(comment.body)
        if (trigger_found and not str(comment.id) in REPLIED_COMMENTS):
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
                done_id = post_comment(comment, url + BOT_BY)
                comment_id.append(str(done_id))
    if comment_id:
        replied_file(comment_id)
    print("Done!")

if __name__ == "__main__":
    main()
