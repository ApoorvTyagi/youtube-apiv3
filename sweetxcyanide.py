'''GET video statistics using youtube api v3 and update the video's metadata'''


#importing all required liberaries
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import logging
import time
from apiclient.discovery import build

# Setting Up Logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

# Set up YouTube credentials
DEVELOPER_KEY = ""  # Your Developer Key
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CHANNEL_ID = ""     # Put your YT channel Id here

youtube = build(
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY,
    cache_discovery=False,
)

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = (
    "client_secret.json"  # This json file you will get from youtube api dashboard
)

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes
)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials, cache_discovery=False
)


def youtubeSearch(query):
    logger.info("Inside youtube search")
    search_response = (
        youtube.search()
        .list(
            q=query,
            type="video",
            order="viewCount",
            part="id,snippet",
            channelId=CHANNEL_ID,
        )
        .execute()
    )

    logger.info("Search Completed...")
    print("Total results: {0}".format(search_response["pageInfo"]["totalResults"]))
    return search_response


def storeResults(response):

    # create variables to store your values
    channelId = []
    viewCount = []
    likeCount = []
    commentCount = []

    logger.info("Storing new search results")

    for search_result in response.get("items", []):
        if (
            search_result["id"]["kind"] == "youtube#video"
            and search_result["id"]["videoId"] == ""        # Put your video id for which you want to get and store stats
        ):

            # append title and video for each item
            videoId.append(search_result["id"]["videoId"])

            # then collect stats on each video using videoId
            stats = (
                youtube.videos()
                .list(part="statistics, snippet", id=search_result["id"]["videoId"])
                .execute()
            )

            channelId.append(stats["items"][0]["snippet"]["channelId"])
            viewCount.append(stats["items"][0]["statistics"]["viewCount"])

            # Not every video has likes/dislikes enabled so they won't appear in JSON response
            try:
                likeCount.append(stats["items"][0]["statistics"]["likeCount"])
            except:
                # Good to be aware of Channels that turn off their Likes
                # Appends "Not Available" to keep dictionary values aligned
                likeCount.append("Not available")

            # Sometimes comments are disabled so if they exist append, if not append nothing...
            # It's not uncommon to disable comments, so no need to wrap in try and except
            if "commentCount" in stats["items"][0]["statistics"].keys():
                commentCount.append(stats["items"][0]["statistics"]["commentCount"])
            else:
                commentCount.append(0)

    # Break out of for-loop and store lists of values in dictionary
    youtube_dict = {
        "channelId": channelId,
        "videoId": videoId,
        "likeCount": likeCount,
        "commentCount": commentCount,
    }

    return youtube_dict


def getDetails():
    # Run YouTube Search
    query = "" #Your YT channel name[ remeber Name !ID ;)]
    response = youtubeSearch(query)
    results = storeResults(response)
    return results


def getMetaData():
    results = getDetails()
    # Replace xyz with your same video id for which you got the stats
    view_count = results.get("viewCount")[results.get("videoId").index("xyz")]
    likes = results.get("likeCount")[results.get("videoId").index("xyz")]
    comments = results.get("commentCount")[results.get("videoId").index("xyz")]
    print(view_count, likes, comments)
    return view_count, likes


def changeTitle(new_title):
    request = youtube.videos().update(
        part="snippet,status",
        body={
            "id": "pJMTlRzlTmc",
            "snippet": {
                "categoryId": 20, # Every video has a category, for example 20 is for video games
                "defaultLanguage": "en", # Your video's language
                "description": desc, # Put new description
                "tags": [], # Add comma seperated tags here
                "title": new_title,
            },
            "status": {"privacyStatus": "public"}, # By default privacy status is private  
        },
    )
    res = request.execute()
    print(res)


oldViews = 0
def main():
    newViews, likes = getMetaData()
    if int(newViews) > oldViews:
        logger.info("Views Increased...")
        oldViews = int(newViews)
        oldLikes = int(likes)
        new_title = "This video has {} views".format(newViews)
        try:
            changeTitle(new_title)
        except:
            logger.info("Error occured in updating title")

if __name__ == "__main__":
    main()
