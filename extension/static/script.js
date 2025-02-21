document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("screenshotBtn");
  const fullPageCheckbox = document.getElementById("captureFull");

  if (!button) {
      console.error("Button not found!");
      return;
  }

  button.addEventListener("click", async () => {
      try {
          const fullPage = fullPageCheckbox.checked;
          const dataUrl = fullPage ? await fullPageScreenshot() : await visibleScreenshot();
          if (!dataUrl) throw new Error("Failed to capture screenshot");

          await uploadAndProcessScreenshot(dataUrl);
      } catch (error) {
          console.error("Screenshot Error:", error);
      }
  });
});

async function visibleScreenshot() {
  return new Promise((resolve, reject) => {
      chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
          if (chrome.runtime.lastError || !dataUrl) {
              reject("Failed to capture visible tab");
          } else {
              resolve(dataUrl);
          }
      });
  });
}

async function fullPageScreenshot() {
  return new Promise((resolve, reject) => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (!tabs.length || !/^https?:\/\//.test(tabs[0].url)) {
              reject("Full-page screenshot not allowed on this page.");
              return;
          }

          chrome.scripting.executeScript(
              {
                  target: { tabId: tabs[0].id },
                  function: scrollAndCapture
              },
              (results) => {
                  if (chrome.runtime.lastError) {
                      reject("Error executing script: " + chrome.runtime.lastError.message);
                  } else if (!results || !results[0]?.result) {
                      reject("Failed to capture full-page screenshot");
                  } else {
                      resolve(results[0].result);
                  }
              }
          );
      });
  });
}

async function scrollAndCapture() {
  const originalScrollY = window.scrollY;
  window.scrollTo({ top: 0, behavior: "smooth" });
  await new Promise((resolve) => setTimeout(resolve, 800));

  const fullHeight = document.documentElement.scrollHeight;
  const viewportHeight = window.innerHeight;
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");

  let yOffset = 0;
  let images = [];

  while (yOffset < fullHeight) {
      window.scrollTo({ top: yOffset, behavior: "smooth" });
      await new Promise((resolve) => setTimeout(resolve, 600));

      const dataUrl = await new Promise((resolve) => {
          chrome.runtime.sendMessage({ action: "capture_screenshot" }, resolve);
      });

      if (!dataUrl) return null;

      images.push(dataUrl);
      yOffset += viewportHeight;
  }

  window.scrollTo({ top: originalScrollY, behavior: "smooth" });

  const firstImg = new Image();
  firstImg.src = images[0];
  await new Promise((resolve) => (firstImg.onload = resolve));

  canvas.width = firstImg.width;
  canvas.height = images.length * firstImg.height;

  let yPosition = 0;
  for (const imgSrc of images) {
      const img = new Image();
      img.src = imgSrc;
      await new Promise((resolve) => (img.onload = resolve));

      ctx.drawImage(img, 0, yPosition);
      yPosition += img.height;
  }

  return canvas.toDataURL("image/png");
}

async function uploadAndProcessScreenshot(dataUrl) {
  const blob = await fetch(dataUrl).then(res => res.blob());
  const formData = new FormData();
  formData.append("file", blob, "screenshot.png");

  try {
      const response = await fetch("https://anishot.onrender.com/apply", {
          method: "POST",
          body: formData
      });

      if (!response.ok) throw new Error("Failed to receive processed image");

      const processedBlob = await response.blob();
      const processedBlobUrl = URL.createObjectURL(processedBlob);

      const timestamp = Date.now();
      chrome.downloads.download({
          url: processedBlobUrl,
          filename: `anishot_${timestamp}.png`,
          saveAs: true
      });

      console.log("Processed screenshot saved locally as anishot_" + timestamp + ".png");
  } catch (error) {
      console.error("Upload failed:", error);
  }
}
