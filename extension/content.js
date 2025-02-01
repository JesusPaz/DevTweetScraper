let autoSaveEnabled = false; // Default state

// Load the initial state from storage
chrome.storage.sync.get("autoSaveEnabled", (data) => {
  autoSaveEnabled = data.autoSaveEnabled || false;
  console.log(`🚀 Auto-Save initialized: ${autoSaveEnabled}`);
});

function getVisibleTweets() {
  console.log("🔍 Searching for tweets on the page...");
  let tweets = [];
  let tweetElements = document.querySelectorAll("article");

  console.log(`📌 Found ${tweetElements.length} tweets on the page.`);

  tweetElements.forEach((tweet, index) => {
    try {
      console.log(`🔹 Processing tweet #${index + 1}...`);

      // Usuario original del tweet
      let user =
        tweet.querySelector('[dir="ltr"] span')?.innerText || "Unknown";

      // Texto del tweet
      let text =
        tweet.querySelector('[data-testid="tweetText"]')?.innerText ||
        "No text";

      // Cantidad de likes
      let likes = tweet.querySelector('[data-testid="like"]')?.innerText || "0";

      // Cantidad de retweets
      let retweets =
        tweet.querySelector('[data-testid="retweet"]')?.innerText || "0";

      // Cantidad de vistas (si está disponible)
      let views =
        tweet.querySelector('[data-testid="viewCount"]')?.innerText || "0";

      // Imagen del perfil del usuario
      let profileImage = tweet.querySelector("img")?.src || "No image";

      // Link al tweet
      let tweetLinkElement = tweet.querySelector(
        'a[role="link"][href*="/status/"]'
      );
      let tweetLink = tweetLinkElement
        ? `https://x.com${tweetLinkElement.getAttribute("href")}`
        : "No link";

      // ID del tweet
      let tweetId = tweetLinkElement
        ? tweetLinkElement.getAttribute("href").split("/status/")[1]
        : "No ID";

      if (tweetId === "No ID") {
        console.warn("⚠️ Tweet without a valid ID was skipped.");
        return;
      }

      // Crear objeto con los datos capturados
      let tweetData = {
        id: tweetId,
        user: user,
        text: text,
        likes: parseInt(likes.replace(",", "")) || 0,
        retweets: parseInt(retweets.replace(",", "")) || 0,
        views: parseInt(views.replace(",", "")) || 0,
        link: tweetLink,
        profileImage: profileImage,
      };

      console.log("✅ Tweet captured:", tweetData);
      tweets.push(tweetData);
    } catch (error) {
      console.error("❌ Error capturing tweet:", error);
    }
  });

  console.log(`📊 Total tweets captured: ${tweets.length}`);
  return tweets;
}

// Function to save tweets, ensuring no duplicates
function saveTweets() {
  const newTweets = getVisibleTweets();

  // Retrieve existing tweets from localStorage
  chrome.storage.local.get("tweets", (data) => {
    const savedTweets = data.tweets || {};
    console.log("📥 Loaded existing tweets from storage:", savedTweets);

    // Merge new tweets into existing ones
    newTweets.forEach((tweet) => {
      savedTweets[tweet.id] = tweet; // Use tweet ID as the key to prevent duplicates
    });

    // Save updated tweets back to localStorage
    chrome.storage.local.set({ tweets: savedTweets }, () => {
      console.log("✅ Tweets auto-saved locally:", savedTweets);
    });
  });
}

// Monitor scroll events to save tweets if auto-save is enabled
if (autoSaveEnabled) {
  window.addEventListener("scroll", () => {
    saveTweets();
  });
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("📩 Message received in content script:", request);

  if (request.action === "toggleAutoSave") {
    autoSaveEnabled = request.enabled;
    console.log(`🚀 Auto-Save toggled: ${autoSaveEnabled}`);

    // Add or remove scroll listener based on toggle
    if (autoSaveEnabled) {
      window.addEventListener("scroll", saveTweets);
    } else {
      window.removeEventListener("scroll", saveTweets);
    }
  }

  return true;
});
