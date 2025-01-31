import asyncio
from twikit import Client
import json
from datetime import datetime
import pandas as pd

# Initialize client with language
client = Client('en-US')

async def auth_with_cookies():
    """Authenticate using cookies"""
    try:
        # Load cookies from file (you'll need to save your cookies in a json file)
        with open('twitter_cookies.json', 'r') as f:
            cookies = json.load(f)
        
        # Set cookies
        await client.login_with_cookie(cookies)
        print("Successfully authenticated with cookies")
        return True
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False

async def search_tech_tweets():
    """Search for tech-related tweets and analyze them"""
    # List of tech-related search terms
    tech_terms = [
        "tech news",
        "artificial intelligence",
        "programming",
        "technology",
        "software development",
        "#tech"
    ]
    
    all_tweets = []
    
    for term in tech_terms:
        try:
            print(f"Searching for: {term}")
            # Search for latest tweets
            tweets = await client.search_tweet(term, 'Latest')
            
            for tweet in tweets:
                # Extract relevant information
                tweet_data = {
                    'created_at': tweet.created_at,
                    'text': tweet.text,
                    'user_name': tweet.user.name,
                    'user_username': tweet.user.username,
                    'followers_count': tweet.user.followers_count,
                    'retweet_count': tweet.retweet_count,
                    'like_count': tweet.like_count,
                    'reply_count': tweet.reply_count,
                    'quote_count': tweet.quote_count,
                    'search_term': term
                }
                
                # Only include tweets from users with significant following
                if tweet.user.followers_count > 1000:
                    all_tweets.append(tweet_data)
                    
        except Exception as e:
            print(f"Error searching for {term}: {e}")
            continue
    
    return all_tweets

async def get_trending_tech():
    """Get trending tech topics"""
    try:
        trends = await client.get_trends('trending')
        tech_trends = [trend for trend in trends if any(tech_word in trend.name.lower() 
                      for tech_word in ['tech', 'ai', 'programming', 'software', 'digital'])]
        return tech_trends
    except Exception as e:
        print(f"Error getting trends: {e}")
        return []

async def main():
    # Authenticate
    if not await auth_with_cookies():
        return
    
    # Get tweets
    tweets = await search_tech_tweets()
    
    # Convert to DataFrame
    df = pd.DataFrame(tweets)
    
    # Sort by engagement (likes + retweets)
    df['total_engagement'] = df['like_count'] + df['retweet_count']
    df = df.sort_values('total_engagement', ascending=False)
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    df.to_csv(f'tech_tweets_{timestamp}.csv', index=False)
    
    # Print most popular tweets
    print("\nMost Popular Tech Tweets:")
    for _, tweet in df.head(10).iterrows():
        print(f"\nUser: {tweet['user_name']} (@{tweet['user_username']})")
        print(f"Followers: {tweet['followers_count']}")
        print(f"Tweet: {tweet['text']}")
        print(f"Engagement: {tweet['total_engagement']} (Likes: {tweet['like_count']}, Retweets: {tweet['retweet_count']})")
        print("-" * 80)
    
    # Get trending topics
    trends = await get_trending_tech()
    if trends:
        print("\nTrending Tech Topics:")
        for trend in trends:
            print(f"- {trend.name}: {trend.tweet_volume} tweets")

if __name__ == "__main__":
    asyncio.run(main())