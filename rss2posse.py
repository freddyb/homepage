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

class Target():
  def __init__(self, config):
    self.config = config
  def send_plain_text(self, text: str):
    pass

class BlueSkyTarget(Target):
  def __init__(self, bskycfg: dict):
    self.name = f"BlueSky({bskycfg['username']})"
    from bsky_bridge import BskySession
    self.session = BskySession(bskycfg['username'], bskycfg['password'])
  def send_plain_text(self, text: str):
    from bsky_bridge import post_text
    post_text(self.session, text)

class MastodonTarget:
  def __init__(self):
    self.name = "Mastodon()"
    from mastodon import Mastodon
    ## This is tricky and wrong for our config abstraction
    ## We don't want a text file in this API. But let's keep it because for now
    # Also: we have done a lot of setup and clearly any other user wouldnt have.
    self.session =  Mastodon(access_token = "mastodon_user.secret")
  def send_plain_text(self, text: str):
    self.session.toot(text)

def prompt_article(i: int, length: int, article: dict) -> str | None:
  print(f"{bcolors.BOLD}Do you want to syndicate the following article? ({i}/{length})")
  print(" Title:", article.get('title', ''))
  print(" Date:", article.get('published', ''))
  print("")
  print("The suggested blurb is as follows (but may be shortened by syndication target)")
  print(f">>>{bcolors.OKGREEN}")
  if hasattr(article, "blurb"):
    print(f"  {article.get('blurb')}")
  else:
    clean_summary = nh3.clean(article.get('summary', ''), tags=set()).replace("\n"," ").strip()
    article['blurb'] = f"{article.get('title', '')} ({article.get('link', '')}): {clean_summary}"
    print(article['blurb'])
  print(f"<<<{bcolors.ENDC}")
  # TODO: a stop-signal would be cool so it can continue posting but stop asking for the rest.
  print(f"{bcolors.OKBLUE}{bcolors.BOLD}({i}/{length}) Publish? [y,N,e,r,q?]{bcolors.ENDC}",)
  choice = input().lower()
  if choice == "?":
    print(f"{bcolors.FAIL}These are your choices:")
    print("y = Yes, use this text.")
    print("n = No, skip this article. (Default.)")
    print("e = Use the text but let me edit first (will prompt again")
    print("r = Please reset the text to the default suggestion (will prompt again)")
    print("? = Print this text.")
    print("q = Quit immediately.")
    print("x = Easter eggs.", bcolors.ENDC)
    return prompt_article(i, length, article)
  elif choice == "y":
    return article.get('blurb', '')
  elif choice == "e": # recurse to prompt for additional input
    print("Please type your input below.")
    article['blurb'] = input()
    return prompt_article(i, length, article)
  elif choice == "r": # reset to link+summary
    delattr(article, "blurb")
    return prompt_article(i, length, article)
  elif choice == "n":
    return None
  elif choice == "q":
    sys.exit(1)
  elif choice == "x":
    print("""Oh. You just found three Easter Eggs.
           .-.
     ..==./xxx\
    /<<<<<\\    |
    \\>>>>>/xxxx/--.
     `'==''---; * *`\
              \\* * */
               '--'`)""")
  else:
      return None


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  # TODO: With '=' as a delimiter, we can't have titles with quotes
  # ... we should escape/remove equal signs from `article.title`.
  # ... access once into `article_title` and then escape there.
  config = configparser.ConfigParser(delimiters=('='))
  config.read('rss2posse.ini')
  if len(sys.argv) > 1 and sys.argv[1] == "--purge-cache":
    config.remove_section("cache")
    with open('rss2posse.ini', 'w') as configfile:
      config.write(configfile)
    logging.info("OK. Article cache was removed.")
    sys.exit(0)
  # FIXME take from config.
  feedpath = "output/feeds/all.atom.xml"
  feed = feedparser.parse(feedpath)
  logging.info(f"Parsed feed at {feedpath} with title '{feed.feed.title}' and {len(feed.entries)} entries.")
  NOW = datetime.datetime.now(datetime.timezone.utc)
  length = len(feed.entries)

  # Initialize targets
  targets = list()
  if 'bluesky' in config:
    logging.info("Bluesky config found.")
    targets.append(BlueSkyTarget(config['bluesky']))
  if 'mastodon' in config:
    logging.info("Mastodon config found.")
    targets.append(MastodonTarget())
  logging.info(f"Initialized {len(targets)} targets.")

  # Going through feed entries.
  for i, article in enumerate(feed.entries):
    if not 'cache' in config.sections():
      config.add_section("cache")
    cached = config['cache'].get(article.title, None)
    if cached and (cached.startswith("SKIP") or cached.startswith("SENT")):
      logging.info(f"Article was cached '{article.title}': {repr(cached)}.")
      continue
    age = NOW - datetime.datetime.fromisoformat(article.published)
    if (age.days > 365):
        logging.debug(f"Skipping old article '{article.title}' without asking.")
        config['cache'][article.title] = "SKIP"
        continue
    text = prompt_article(i, length, article)
    if text is None:
      logging.info(f"Skipping article '{article.title}' by user request.")
      config['cache'][article.title] = "SKIP"
      # remember not to post this one.
      # config.write...
    else: # post.
      logging.info(f"Submitting '{article.title}'.")
      for target in targets:
        print("For target x out of y. This is the text. We are not actually sending.")
        print(text)
        try:
          target.send_plain_text(text)
          config['cache'][article.title] = "SENT " + datetime.datetime.now().isoformat()
        except Exception:
          logging.error(f"Failed sending '{article.title}' to {target.name}.")
          config['cache'][article.title] = "FAILED " + datetime.datetime.now().isoformat()

  with open('rss2posse.ini', 'w') as configfile:
    config.write(configfile)
