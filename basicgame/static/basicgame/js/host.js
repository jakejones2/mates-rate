import { makeID, refreshPage, addExpiration } from "./base.js";

refreshPage();

const validator = document.getElementById("form-error");
const hostForm = document.getElementById("host-form");
const nicknameInput = document.getElementById("nickname");
const gameNameInput = document.querySelector("#game-name-input");
const playerNameInput = document.getElementById("player-name-input");
const cyclesInput = document.getElementById("num-of-cycles");
const button = document.getElementById("custom-submit");
const spinner = document.getElementById("spinner");
const gameName = JSON.parse(document.getElementById("game-name").textContent);
const philosopher = document.getElementById("philosopher");
const helpButton = document.getElementById("help-button");
const helpText = document.getElementById("help-text");
const closeHelpButton = document.getElementById("close-help");

nicknameInput.focus();
gameNameInput.value = gameName;

button.onclick = () => {
  button.style.display = "none";
  spinner.style.display = "block";
};

function validate(warning) {
  button.style.display = "block";
  spinner.style.display = "none";
  validator.style.display = "block";
  validator.innerHTML = warning;
  setTimeout(function () {
    validator.style.display = "none";
  }, 3000);
}

hostForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const nickname = nicknameInput.value;
  if (nickname.length < 1) {
    validator.style.display = "block";
    validator.innerHTML = "Enter a nickname!";
    setTimeout(function () {
      validator.style.display = "none";
    }, 3000);
  }
  if (/[^1-9]{1}/g.test(cyclesInput.value) || !cyclesInput.value) {
    validate("Enter a number between 1 and 9");
  } else if (nickname.length < 1) {
    validate("Enter a longer nickname...");
  } else {
    const playerName = nickname + makeID(8);
    const cookie = `${gameName}=${playerName}`;
    document.cookie = addExpiration(cookie);
    playerNameInput.value = playerName;
    hostForm.submit();
  }
});

philosopher.onclick = () => {
  window.location = "/";
};

helpButton.onclick = function (e) {
  helpText.style.display = "block";
};

closeHelpButton.onclick = function (e) {
  helpText.style.display = "none";
};
