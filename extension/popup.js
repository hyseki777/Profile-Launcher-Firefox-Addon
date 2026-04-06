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
    let btnContainer = document.createElement("div");
    btnContainer.style.display = "flex";
    btnContainer.style.gap = "8px";

    let btn1 = document.createElement("button");
    btn1.textContent = "Create";
    btn1.addEventListener("click", () => toggleButton("Create"));

    let btn2 = document.createElement("button");
    btn2.textContent = "Rename";
    btn2.addEventListener("click", () => toggleButton("Rename"));

    let btn3 = document.createElement("button");
    btn3.textContent = "Delete";
    btn3.addEventListener("click", () => toggleButton("Delete"));

    btnContainer.appendChild(btn1);
    btnContainer.appendChild(btn2);
    btnContainer.appendChild(btn3);
    list.appendChild(btnContainer);
  }
}


function toggleButton(btname) {
  if (document.getElementById("dynamicInput")) {
    location.reload();
  } else {
    const container = document.createElement("div");
    container.className = "toggle-container";
    container.style.display = "flex";
    container.style.alignItems = "flex-start";
    container.style.gap = "12px";

    function makeInput(id, placeholder) {
      const input = document.createElement("input");
      input.type = "text";
      input.id = id;
      input.placeholder = placeholder;
      return input;
    }

    let input1 = makeInput("dynamicInput", "Profile name");
    let input2 = null;

    const inputWrapper = document.createElement("div");
    inputWrapper.style.display = "flex";
    inputWrapper.style.flexDirection = "column";
    inputWrapper.style.gap = "6px";

    inputWrapper.appendChild(input1);

    if (btname === "Rename") {
      input2 = makeInput("dynamicInput2", "New profile name");
      inputWrapper.appendChild(input2);
    }

    let deleteCheckbox = null;
    if (btname === "Delete") {
      deleteCheckbox = document.createElement("input");
      deleteCheckbox.type = "checkbox";
      deleteCheckbox.id = "deleteFilesCheckbox";

      const label = document.createElement("label");
      label.htmlFor = "deleteFilesCheckbox";
      label.textContent = "Delete Files?";
      label.style.color = "white"

      const checkboxWrapper = document.createElement("div");
      checkboxWrapper.style.display = "flex";
      checkboxWrapper.style.alignItems = "center";
      checkboxWrapper.style.gap = "4px";
      checkboxWrapper.appendChild(deleteCheckbox);
      checkboxWrapper.appendChild(label);

      inputWrapper.appendChild(checkboxWrapper);
    }

    container.appendChild(inputWrapper);

    const btn = document.createElement("button");
    btn.textContent = btname + " Profile";
    btn.id = "dynamicButton";
    btn.addEventListener("click", async () => {
      let profileValue = input1.value.trim();
      let newValue = input2 ? input2.value.trim() : null;
      let deleteFiles = deleteCheckbox ? deleteCheckbox.checked : false;

      let result = await sendNativeMessage({
        command: btname,
        profile: profileValue,
        newProfile: newValue,
        deleteFiles: deleteFiles
      });
      location.reload();
    });

    container.appendChild(btn);
    toggleArea.appendChild(container);

    input1.focus();

    [input1, input2].forEach(inp => {
      if (inp) {
        inp.addEventListener("keypress", function(event) {
          if (event.key === "Enter") {
            event.preventDefault();
            btn.click();
          }
        });
      }
    });
  }
}

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

