import { getCookie, makeID, refreshPage, addExpiration } from "./base.js";

refreshPage();

const nicknameInput = document.querySelector("#nickname");
const gameName = document.querySelector("#game-name");
const playerNameInput = document.querySelector("#player-name");
const joinForm = document.querySelector("#join-form");
const button = document.getElementById("custom-submit");
const spinner = document.getElementById("spinner");
const validator = document.getElementById("form-error");
const philosopher = document.getElementById("philosopher");
const helpButton = document.getElementById("help-button");
const helpText = document.getElementById("help-text");
const closeHelpButton = document.getElementById("close-help");

button.onclick = () => {
  button.style.display = "none";
  spinner.style.display = "block";
};

// handle form - convert nickname into playername (nickname + id)
joinForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const gameNameValidated = gameName.value.toLowerCase().replace("-", "_");
  const nickname = nicknameInput.value.trim().replace("-", "_");
  const oldCookieAndPlayerName = getCookie(gameNameValidated);

  // if a player tries to join game twice, they keep the same cookie.
  // allows players to rejoin mid game
  let cookie;
  let playerName;
  if (oldCookieAndPlayerName.playerName.includes(nickname)) {
    cookie = oldCookieAndPlayerName.cookie;
    playerName = oldCookieAndPlayerName.playerName;
  } else {
    playerName = nickname + makeID(8);
    cookie = `${gameNameValidated}=${playerName}`;
  }

  document.cookie = addExpiration(cookie);
  playerNameInput.value = playerName;
  joinForm.submit();
});

philosopher.onclick = () => {
  window.location = "/";
};

// show any errors for 3 seconds
validator.style.display = "block";
setTimeout(function hideError() {
  validator.style.display = "none";
}, 3000);

nicknameInput.focus();

helpButton.onclick = function (e) {
  helpText.style.display = "block";
};

closeHelpButton.onclick = function (e) {
  helpText.style.display = "none";
};
