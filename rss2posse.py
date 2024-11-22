import configparser
import logging
import feedparser
import sys
import datetime
import nh3

#Thank you stackoverflow.
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


logging.basicConfig(level=logging.DEBUG)

class ConfigReader:
    def __init__(self):
        pass
    def read_config(self, filename):
        parser = configparser.ConfigParser()
        try:
            parser.read(filename)
            # parse only those sections and options that have values
            result = {}
            for section in parser.sections():
                result[section] = {option: value for option, value in parser.options(section) if value}
            return result
        except Exception as e:
            print(f"Error reading configuration file: {e}")
            return None

class Target():
  def __init__(self, config):
    self.config = config
  def send_plain_text(self, text):
    pass

class BlueSkyTarget(Target):
  def __init__(self, bskycfg):
    from bsky_bridge import BskySession
    self.session = BskySession(bskycfg['username'], bskycfg['password'])
  def send_plain_text(self, text):
    from bsky_bridge import post_text
    post_text(self.session, text)

class MastodonTarget:
  def __init__(self):
    from mastodon import Mastodon
    ## This is tricky and wrong for our config abstraction
    ## We don't want a text file in this API. But let's keep it because for now
    # Also: we have done a lot of setup and clearly any other user wouldnt have.
    self.session =  Mastodon(access_token = "mastodon_user.secret")
  def send_plain_text(self, text):
    self.session.toot(text)

def prompt_article(i, l, article):
  print(f"{bcolors.OKGREEN}Do you want to syndicate the following article? ({i}/{l})")
  print(" Title: ", article.title)
  print(" Date: ", article.published)
  print("")
  print("The suggested blurb is as follows (but may be shortened by syndication target)")
  print(">>>")
  if hasattr(article, "blurb"):
    print(f"  {article.blurb}")
  else:
    clean_summary = nh3.clean(article.summary, tags=set()).replace("\n"," ").strip()
    article.blurb = f"  {article.title} ({article.link}): {clean_summary}"
    print(article.blurb)
  print("<<<")
  print(f"{bcolors.OKBLUE}{bcolors.BOLD}({i}/{l}) Publish? [y,N,e,r,q?]{bcolors.ENDC}",)
  choice = input().lower()
  if choice == "?":
    print(f"{bcolors.FAIL}These are your choice")
    print("y = Yes, use this text.")
    print("n = No, skip this article.")
    print("e = Use the text but let me edit first (will prompt again")
    print("r = Please reset the text to the default suggestion (will prompt again)")
    print("? = Print this text.")
    print("q = Quit immediately.")
    print("x = Easter eggs.", bcolors.ENDC)
    return prompt_article(i, l, article)
  elif choice == "y":
    return article.blurb
  elif choice == "e": # recurse to prompt for additional input
    print("Please type your input below.")
    article.blurb = input()
    return prompt_article(i, l, article)
  elif choice == "r": # reset to link+summary
    delattr(article, "blurb")
    return prompt_article(i, l, article)
  elif choice == "n":
    return None
  elif choice == "q":
    sys.exit(1)
  elif choice == "x":
    print("""Oh. You just found three Easter Eggs.
           .-.
     ..==./xxx\
    /<<<<<\    |
    \>>>>>/xxxx/--.
     `'==''---; * *`\
              \* * */
               '--'`)""")
  else:
      return None




if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)

  config = configparser.ConfigParser()

  config.read('rss2posse.ini')

  # FIXME take from config.
  feedpath = "output/feeds/all.atom.xml"
  feed = feedparser.parse(feedpath)
  logging.info(f"Parsed feed at {feedpath} with title '{feed.feed.title}' and {len(feed.entries)} entries.")
  NOW = datetime.datetime.now(datetime.timezone.utc)

  targets = list()
  if 'bluesky' in config:
    logging.info("Bluesky config found.")
    targets.append(BlueSkyTarget(config['bluesky']))
  if 'mastodon' in config:
    logging.info("Mastodon config found.")
    targets.append(MastodonTarget())
  logging.info(f"Initialized {len(targets)} targets.")
  len = len(feed.entries)
  for i, article in enumerate(feed.entries):
    age = NOW - datetime.datetime.fromisoformat(article.published)
    if (age.days > 365):
        logging.info(f"Skipping old article '{article.title}'.")
        continue
    text = prompt_article(i, len, article)
    if text is not None:
      for target in targets:
        print("For target x out of y. This is the text. We are not actually sending.")
        print(text)
        #target.send_plain_text(text)
