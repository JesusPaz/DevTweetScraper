let autoSaveEnabled = false; // Default state

// Load the initial state from storage
chrome.storage.sync.get("autoSaveEnabled", (data) => {
  autoSaveEnabled = data.autoSaveEnabled || false;
  console.log(`🚀 Auto-Save initialized: ${autoSaveEnabled}`);

  if (autoSaveEnabled) {
    startAutoSave();
  }
});

// URL de la API
const API_URL = "http://127.0.0.1:8000/tweets";

// Cola de tweets por enviar
const tweetQueue = [];

// Set para guardar los IDs de los tweets ya enviados
const sentTweetIds = new Set();

// Función para obtener tweets visibles
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
      const likes =
        tweet.querySelector('[data-testid="like"]')?.innerText || "0";
      const retweets =
        tweet.querySelector('[data-testid="retweet"]')?.innerText || "0";
      const views =
        tweet.querySelector('[data-testid="viewCount"]')?.innerText || "0";
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

      const createdAt = new Date().toISOString();

      const tweetData = {
        tweet_id: tweetId,
        user: { username: user, followers: 0 },
        text: text,
        likes: parseInt(likes.replace(",", "")) || 0,
        retweets: parseInt(retweets.replace(",", "")) || 0,
        views: parseInt(views.replace(",", "")) || 0,
        link: tweetLink,
        profile_image: profileImage,
        created_at: createdAt,
        sent_by_user: "my_extension",
      };

      tweets.push(tweetData);
    } catch (error) {
      console.error("❌ Error capturing tweet:", error);
    }
  });

  return tweets;
}

// Función para enviar tweets acumulados
function sendTweetsFromQueue() {
  if (tweetQueue.length === 0) return; // Si no hay tweets, no hacer nada

  const tweetsToSend = [...tweetQueue];
  tweetQueue.length = 0; // Limpiar la cola antes de enviar

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
      console.log("✅ Tweets successfully sent to the API:", data);

      // Agregar los IDs de los tweets enviados al set
      tweetsToSend.forEach((tweet) => sentTweetIds.add(tweet.tweet_id));
    })
    .catch((error) => {
      console.error("❌ Error sending tweets to the API:", error);

      // Si ocurre un error, devolver los tweets a la cola
      tweetQueue.push(...tweetsToSend);
    });
}

// Función para manejar el scroll y acumular tweets
function handleScroll() {
  const now = Date.now();
  const tweets = getVisibleTweets();

  tweets.forEach((tweet) => {
    if (!sentTweetIds.has(tweet.tweet_id)) {
      tweetQueue.push(tweet);
    }
  });
}

// Iniciar el proceso de envío automático cada X segundos
function startAutoSave() {
  window.addEventListener("scroll", handleScroll);

  setInterval(() => {
    sendTweetsFromQueue();
  }, 5000); // Enviar cada 5 segundos
}

// Detener el auto-guardado
function stopAutoSave() {
  window.removeEventListener("scroll", handleScroll);
}

// Escuchar mensajes desde el popup
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
