function sendNativeMessage(msg) {
  let label = document.getElementById("idLabel").textContent;
  label = label.split("Browser ID: ")[1]
  if (label != "" && label != "Default")
    return browser.runtime.sendNativeMessage("profile_launcher_" + label, msg).catch(error => document.getElementById("idLabel").textContent = error);
  return browser.runtime.sendNativeMessage("profile_launcher", msg).catch(error => document.getElementById("idLabel").textContent = error);

}

async function loadProfiles() {
  let response = await sendNativeMessage({ command: "list" });
  let list = document.getElementById("profiles");

  list.innerHTML = "";
  response.profiles.forEach(profile => {
    let li = document.createElement("li");
    let btn = document.createElement("button");
    btn.textContent = profile;
    btn.addEventListener("click", async () => {
      let result = await sendNativeMessage({ command: "launch", profile: profile });
    });
    li.appendChild(btn);
    list.appendChild(li);
  });
  if (navigator.platform.toLowerCase().includes("linux")) {
    let btn = document.createElement("button");
    btn.id = "toggleBtn"
    btn.textContent = "+";
    btn.addEventListener("click", toggleCreate);
    list.appendChild(btn);
  }
}


function toggleCreate() {
  if (document.getElementById("dynamicInput")) {
    location.reload();
  } else {
    const container = document.createElement("div");
    container.className = "toggle-container";

    const input = document.createElement("input");
    input.type = "text";
    input.id = "dynamicInput";
    input.placeholder = "New profile name";

    const btn = document.createElement("button");
    btn.textContent = "Create Profile";
    btn.id = "dynamicButton";
    btn.addEventListener("click", async () => {
      let result = await sendNativeMessage({ command: "create", profile: input.value.trim() });
      location.reload();
    });

    container.appendChild(input);
    container.appendChild(btn);
    toggleArea.appendChild(container);
    input.focus()
    input.addEventListener("keypress", function(event) {
      if (event.key === "Enter") {
        event.preventDefault();
        btn.click();
      }
    });
  }
};


document.addEventListener("DOMContentLoaded", async () => {
  const idLabel = document.getElementById("idLabel");
  const idInput = document.getElementById("idInput");
  const idSetButton = document.getElementById("idSetButton");
  const idResetButton = document.getElementById("idResetButton");

  idInput.focus();
  idInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      idSetButton.click();
    }
  });

  let stored = await browser.storage.local.get("BrowserID");
  if (!stored.BrowserID) {
    await browser.storage.local.set({ BrowserID: "Default" });
    stored = await browser.storage.local.get("BrowserID");
  }
  idLabel.textContent = "Browser ID: " + stored.BrowserID;
  idInput.value = "";

  idSetButton.addEventListener("click", async () => {
    let value = idInput.value.trim();
    if (value) {
      idLabel.textContent = "Browser ID: " + value;
      idInput.value = "";
      await browser.storage.local.set({ BrowserID: value });
    } else
      resetID();
    loadProfiles();
  });
  idResetButton.addEventListener("click", resetID);
  loadProfiles();

});

async function resetID() {
  let value = "Default";
  idLabel.textContent = "Browser ID: " + value;
  idInput.value = "";
  await browser.storage.local.set({ BrowserID: value });
  loadProfiles();
}

