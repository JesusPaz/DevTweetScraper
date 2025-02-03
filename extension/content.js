let autoSaveEnabled = false;

chrome.storage.sync.get("autoSaveEnabled", (data) => {
  autoSaveEnabled = data.autoSaveEnabled || false;
  if (autoSaveEnabled) {
    startAutoSave();
  }
});

const API_URL = "http://127.0.0.1:8000/tweets";
const tweetQueue = [];
const sentTweetIds = new Set();

function getVisibleTweets() {
  const tweets = [];
  const tweetElements = document.querySelectorAll("article");

  tweetElements.forEach((tweet) => {
    try {
      const user =
        tweet.querySelector('[dir="ltr"] span')?.innerText || "Unknown";
      const text =
        tweet.querySelector('[data-testid="tweetText"]')?.innerText ||
        "No text";
      const profileImage = tweet.querySelector("img")?.src || "No image";
      const tweetLinkElement = tweet.querySelector(
        'a[role="link"][href*="/status/"]'
      );
      const tweetLink = tweetLinkElement
        ? `https://x.com${tweetLinkElement.getAttribute("href")}`
        : "No link";
      const tweetId = tweetLinkElement
        ? tweetLinkElement.getAttribute("href").split("/status/")[1]
        : "No ID";

      if (tweetId === "No ID" || sentTweetIds.has(tweetId)) {
        return;
      }

      // Buscar el div con todas las métricas
      const metricsElement = tweet.querySelector('[aria-label*="views"]');
      let replies = 0,
        reposts = 0,
        likes = 0,
        bookmarks = 0,
        views = 0;

      if (metricsElement) {
        const metricsText = metricsElement.getAttribute("aria-label");

        const repliesMatch = metricsText.match(/(\d+[,.]?\d*)\srepl/i);
        const repostsMatch = metricsText.match(/(\d+[,.]?\d*)\srepost/i);
        const likesMatch = metricsText.match(/(\d+[,.]?\d*)\slike/i);
        const bookmarksMatch = metricsText.match(/(\d+[,.]?\d*)\sbookmark/i);
        const viewsMatch = metricsText.match(/(\d+[,.]?\d*)\sviews/i);

        replies = repliesMatch ? parseInt(repliesMatch[1].replace(",", "")) : 0;
        reposts = repostsMatch ? parseInt(repostsMatch[1].replace(",", "")) : 0;
        likes = likesMatch ? parseInt(likesMatch[1].replace(",", "")) : 0;
        bookmarks = bookmarksMatch
          ? parseInt(bookmarksMatch[1].replace(",", ""))
          : 0;
        views = viewsMatch ? parseInt(viewsMatch[1].replace(",", "")) : 0;
      }

      const createdAt = new Date().toISOString();

      const tweetData = {
        tweet_id: tweetId,
        user: { username: user, followers: 0 },
        text: text,
        likes: likes,
        retweets: reposts, // Reposts son retweets
        views: views,
        replies: replies,
        bookmarks: bookmarks,
        link: tweetLink,
        profile_image: profileImage,
        created_at: createdAt,
        sent_by_user: "my_extension",
      };

      console.log(tweetData);
      tweets.push(tweetData);
    } catch (error) {
      console.error("Error capturing tweet:", error);
    }
  });

  return tweets;
}

function sendTweetsFromQueue() {
  if (tweetQueue.length === 0) return;

  const tweetsToSend = [...tweetQueue];
  tweetQueue.length = 0;

  fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(tweetsToSend),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      tweetsToSend.forEach((tweet) => sentTweetIds.add(tweet.tweet_id));
    })
    .catch((error) => {
      tweetQueue.push(...tweetsToSend);
    });
}

function handleScroll() {
  const tweets = getVisibleTweets();
  tweets.forEach((tweet) => {
    if (!sentTweetIds.has(tweet.tweet_id)) {
      tweetQueue.push(tweet);
    }
  });
}

function startAutoSave() {
  window.addEventListener("scroll", handleScroll);

  setInterval(() => {
    sendTweetsFromQueue();
  }, 5000);
}

function stopAutoSave() {
  window.removeEventListener("scroll", handleScroll);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "toggleAutoSave") {
    autoSaveEnabled = request.enabled;

    if (autoSaveEnabled) {
      startAutoSave();
    } else {
      stopAutoSave();
    }
  }

  sendResponse({ status: "success" });
});
