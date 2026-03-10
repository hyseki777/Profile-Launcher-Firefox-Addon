function sendNativeMessage(msg) {
    console.log(msg);
    return browser.runtime.sendNativeMessage("profile_launcher", msg);
}

async function loadProfiles() {
    let response = await sendNativeMessage({command: "list"}) ;
    let list = document.getElementById("profiles");
    list.innerHTML = "";
    response.profiles.forEach(profile => {
        let li = document.createElement("li");
        let btn = document.createElement("button");
        btn.textContent = profile;
        btn.addEventListener("click", () => {
            sendNativeMessage({command: "launch", profile: profile});
        });
        li.appendChild(btn);
        list.appendChild(li);
    });
}

loadProfiles();
