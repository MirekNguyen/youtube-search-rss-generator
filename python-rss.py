import json
from datetime import datetime, timedelta

import pytz
import rfeed
from feedgen.feed import FeedGenerator
from youtubesearchpython import *

timezone = pytz.timezone("Europe/Prague")

query = input("Search Youtube: ")
customSearch = VideosSearch(query, limit=5)
result = customSearch.result(mode=ResultMode.json)
object = json.loads(result)


# Function to parse relative publishedDate to datetime
def parse_published_date(published_date):
    if "day" in published_date:
        days_ago = int(published_date.split()[0])
        return datetime.now() - timedelta(days=days_ago)
    elif "month" in published_date:
        months_ago = int(published_date.split()[0])
        # Assuming 30 days in a month
        return datetime.now() - timedelta(days=months_ago * 30)
    elif "year" in published_date:
        years_ago = int(published_date.split()[0])
        return datetime.now() - timedelta(days=years_ago * 365)
    else:
        return datetime.now()  # Return current datetime for unknown formats


sorted_videos = sorted(
    object["result"],
    key=lambda video: parse_published_date(video["publishedTime"]),
    # reverse=True,
)

# Print sorted videos
items = []
for video in sorted_videos:
    print(video.get("publishedTime", ""))
    print(video.get("title", ""))
    print(video.get("link", ""))


fg = FeedGenerator()
fg.id("https://mirekng.com/")
fg.title("Youtube subscriptions feed")
fg.subtitle("Youtube subscriptions feed")
fg.link(href="https://mirekng.com", rel="self")
fg.language("en")


for video in sorted_videos:
    fe = fg.add_entry()
    fe.id(video["link"])
    fe.title(video["publishedTime"] + video["title"])
    fe.link(href=video["link"], replace=True)
    fe.description(video["link"])
    pubDate = parse_published_date(video["publishedTime"])
    fe.pubDate(timezone.localize(pubDate))


rssfeed = fg.rss_str(pretty=True)
fg.rss_file("rss.xml")
