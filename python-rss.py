import json
import sys
from datetime import datetime, timedelta

import pytz
from feedgen.feed import FeedGenerator
from youtubesearchpython import ResultMode, VideosSearch

if len(sys.argv) < 2:
    print("No output file or search query provided.")
    exit(1)
elif len(sys.argv) == 2:
    query = input("Search Youtube: ")
elif len(sys.argv) == 3:
    query = sys.argv[1]
else:
    print("Too many arguments")
    exit(1)

timezone = pytz.timezone("Europe/Prague")

customSearch = VideosSearch(query, limit=5)
result = customSearch.result(mode=ResultMode.json)
object = json.loads(result)


# Function to parse relative publishedDate to datetime
def parse_published_date(published_date):
    if "day" in published_date:
        days_ago = int(published_date.split()[0])
        return datetime.now() - timedelta(days=days_ago)
    elif "week" in published_date:
        weeks_ago = int(published_date.split()[0])
        return datetime.now() - timedelta(days=weeks_ago * 7)
    elif "month" in published_date:
        months_ago = int(published_date.split()[0])
        # Assuming 30 days in a month
        return datetime.now() - timedelta(days=months_ago * 30)
    elif "year" in published_date:
        # Assuming 365 days in a year
        years_ago = int(published_date.split()[0])
        return datetime.now() - timedelta(days=years_ago * 365)
    else:
        return datetime.now()  # Return current datetime for unknown formats


sorted_videos = sorted(
    object["result"],
    key=lambda video: parse_published_date(video["publishedTime"]),
)

fg = FeedGenerator()
fg.id("https://mirekng.com/rss/" + sys.argv[len(sys.argv) - 1])
fg.title("Youtube subscriptions feed")
fg.subtitle("Youtube subscriptions feed")
fg.link(href="https://mirekng.com", rel="self")
fg.language("en")

for video in sorted_videos:
    fe = fg.add_entry()
    fe.id(video["link"])
    fe.title(video["publishedTime"] + " | " + video["title"])
    fe.link(href=video["link"], replace=True)
    pubDate = parse_published_date(video["publishedTime"])
    fe.description(
        video["link"]
        + "<br>"
        + video["publishedTime"]
        + "<br>"
        + pubDate.strftime("%FT%T")
    )
    fe.pubDate(timezone.localize(pubDate))

rssfeed = fg.rss_str(pretty=True)
fg.rss_file(sys.argv[len(sys.argv) - 1])
