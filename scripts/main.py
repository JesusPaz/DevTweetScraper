import asyncio
from twikit import Client
import os
import pandas as pd
from datetime import datetime

# Initialize client
client = Client("en-US")


async def authenticate():
    """
    Try to authenticate first with cookies, if not available use credentials.
    """
    cookies_file = "twitter_cookies.json"

    # Try with cookies
    if os.path.exists(cookies_file):
        try:
            print("Attempting to authenticate with saved cookies...")
            client.load_cookies(cookies_file)
            await client.user_id()  # Verify if cookies work
            print("Successfully authenticated with cookies")
            return True
        except Exception as e:
            print(f"Saved cookies are invalid: {e}")

    # If cookies don't work, use credentials
    try:
        print("Authenticating with credentials...")
        USERNAME = os.getenv("TWITTER_USERNAME")
        EMAIL = os.getenv("TWITTER_EMAIL")
        PASSWORD = os.getenv("TWITTER_PASSWORD")

        await client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)

        # Save cookies for future use
        print("Saving cookies for future sessions...")
        client.save_cookies(cookies_file)
        print("Successfully authenticated with credentials and saved cookies")
        return True

    except Exception as e:
        print(f"Authentication failed: {e}")
        return False


async def search_tech_tweets():
    """Search for tech-related tweets and analyze them"""
    tech_terms = ["programming"]
    all_tweets = []

    for term in tech_terms:
        try:
            print(f"Searching for: {term}")
            tweets = await client.search_tweet(term, "Latest")

            for tweet in tweets:
                print(vars(tweet))
                
                user = getattr(tweet, "user", None)
                if not user:
                    continue

                tweet_data = {
                    "created_at": getattr(tweet, "created_at", None),
                    "text": getattr(tweet, "text", None),
                    "user_name": getattr(user, "name", None),
                    "user_screen_name": getattr(user, "screen_name", None),
                    "followers_count": getattr(user, "followers_count", 0),
                    "retweet_count": getattr(tweet, "retweet_count", 0),
                    "like_count": getattr(tweet, "like_count", 0),
                    "reply_count": getattr(tweet, "reply_count", 0),
                    "quote_count": getattr(tweet, "quote_count", 0),
                    "search_term": term,
                }

                if tweet_data["followers_count"] > 1000:
                    all_tweets.append(tweet_data)

        except Exception as e:
            print(f"Error searching for {term}: {e}")
            continue

    return all_tweets


async def main():
    if not await authenticate():
        print("Authentication failed. Please check your credentials.")
        return

    tweets = await search_tech_tweets()

    if tweets:
        # Convert to DataFrame
        df = pd.DataFrame(tweets)
        df["total_engagement"] = df["like_count"] + df["retweet_count"]
        df = df.sort_values("total_engagement", ascending=False)

        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tech_tweets_{timestamp}.csv"
        df.to_csv(filename, index=False)

        print(f"✅ Saved {len(df)} tweets to {filename}")

        # Print most popular tweets
        print("\n🔥 Most Popular Tech Tweets:")
        for _, tweet in df.head(10).iterrows():
            print(f"\nUser: {tweet['user_name']} (@{tweet['user_screen_name']})")
            print(f"Followers: {tweet['followers_count']}")
            print(f"Tweet: {tweet['text']}")
            print(
                f"Engagement: {tweet['total_engagement']} (Likes: {tweet['like_count']}, Retweets: {tweet['retweet_count']})"
            )
            print("-" * 80)
    else:
        print("No tweets found.")


if __name__ == "__main__":
    asyncio.run(main())
