import argparse
import json
import re
import sys
from datetime import datetime, timedelta

import pytz
from feedgen.feed import FeedGenerator
from youtubesearchpython import ResultMode, VideosSearch

timezone = pytz.timezone("Europe/Prague")
parser = argparse.ArgumentParser(description="Generate RSS for Youtube query")

parser.add_argument("-q", "--query", action="store", help="Query (required)")
parser.add_argument(
    "-o", "--output", action="store", help="Output file path (required)"
)
parser.add_argument("-c", "--channel", action="store_true", help="Search videos of specific channel")
args = parser.parse_args()

if not args.query or not args.output:
    print("No output file or search query provided.")
    exit(1)

customSearch = VideosSearch(args.query, limit=10)


result = customSearch.result(mode=ResultMode.json)
object = json.loads(result)


# Function to parse relative publishedDate to datetime
def parse_published_date(published_date):
    if "day" in published_date:
        days_ago = int(re.search(r"\d+", published_date).group())
        return datetime.now() - timedelta(days=days_ago)
    elif "week" in published_date:
        weeks_ago = int(re.search(r"\d+", published_date).group())
        return datetime.now() - timedelta(days=weeks_ago * 7)
    elif "month" in published_date:
        # Assuming 30 days in a month
        months_ago = int(re.search(r"\d+", published_date).group())
        return datetime.now() - timedelta(days=months_ago * 30)
    elif "year" in published_date:
        # Assuming 365 days in a year
        years_ago = int(re.search(r"\d+", published_date).group())
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
    if args.channel and not video['channel']['name'].lower() == args.query.lower():
        continue
    pubDate = parse_published_date(video["publishedTime"])
    if (pubDate < (datetime.now() - timedelta(days=7))):
        continue
    fe = fg.add_entry()
    fe.id(video["link"])
    fe.title(video["publishedTime"] + " | " + video["title"])
    fe.link(href=video["link"], replace=True)
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
