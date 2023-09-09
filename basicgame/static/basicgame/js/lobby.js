import { getCookie, refreshPage } from "./base.js";

const gameName = JSON.parse(document.getElementById("game-name").textContent);
const playerName = getCookie(gameName)["playerName"];
const nickname = playerName.slice(0, playerName.length - 8);
const host = JSON.parse(document.getElementById("game-host").textContent);

const waitMessage = document.getElementById("wait-message");
const gameNameElement = document.querySelector("h2");
const subtitle = document.getElementById("subtitle");
const startGame = document.getElementById("start-game");
const chatLog = document.getElementById("chat-log");
const playerLog = document.getElementById("player-log");
const chatInput = document.getElementById("chat-message-input");
const chatSubmit = document.getElementById("chat-message-submit");
const philosopher = document.getElementById("philosopher");
const spinner = document.getElementById("spinner");
const leave = document.getElementById("leave");
const closeLeave = document.getElementById("close-leave");
const yesLeave = document.getElementById("yes-leave");
const leaveMessage = document.querySelector("p");
const modal = document.getElementById("modal-content");

let websocketAddress;
if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
  websocketAddress =
    "ws://" + window.location.host + "/ws/lobby/" + gameName + "/";
} else {
  websocketAddress =
    "wss://" + window.location.host + "/wss/lobby/" + gameName + "/";
}

const chatSocket = new WebSocket(websocketAddress);

refreshPage();

// display correct page for the host
if (host === playerName) {
  waitMessage.style.display = "block";
  gameNameElement.style.margin = 0;
  subtitle.innerHTML = "Game ID:";
  leaveMessage.innerHTML +=
    " You are the <b>host</b>, so the game cannot proceed without you!";
  modal.style.height = "7em";
} else {
  waitMessage.style.display = "block";
  gameNameElement.style.margin = 0;
  waitMessage.innerHTML = "Waiting for Host...";
}

// UI

chatInput.focus();
chatInput.onkeyup = function (e) {
  // enter, return
  if (e.keyCode === 13) chatSubmit.click();
};

// utils

function chatSend(type, message) {
  const varObject = {};
  varObject[type] = message;
  chatSocket.send(JSON.stringify(varObject));
}

function updatePlayerList(playerList) {
  playerLog.innerHTML = playerList;
  if (playerList.split("\n").length >= 4 && host === playerName) {
    waitMessage.style.display = "none";
    startGame.style.display = "block";
    gameNameElement.style.margin = 0;
  }
}

// event listeners

startGame.onclick = function (e) {
  startGame.style.display = "none";
  spinner.style.display = "block";
  chatSend("startgame", "now");
};

chatSocket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  if (data.message) {
    chatLog.innerHTML += data.message;
  }
  if (data.playerList) {
    updatePlayerList(data.playerList);
  }
  if (data.startGame) {
    window.location.pathname = `/${gameName}/play`;
  }
};

chatSocket.onclose = function (e) {
  setTimeout(() => {
    chatLog.value += "oops - something went wrong! Chat disabled...";
  }, 2000);
};

chatSubmit.onclick = function (e) {
  const message =
    '<span style="font-weight:bold">' +
    nickname +
    ": </span>" +
    chatInput.value +
    "\n";
  chatSend("chat_message", message);
  chatInput.value = "";
};

philosopher.addEventListener("click", () => {
  leave.style.display = "block";
});

closeLeave.addEventListener("click", () => {
  leave.style.display = "none";
});

yesLeave.addEventListener("click", () => {
  window.location = "/";
});

window.addEventListener("click", (event) => {
  if (event.target === leave) {
    leave.style.display = "none";
  }
});

setTimeout(() => {
  const data = chatLog.innerHTML;
  const messages = data.split("<br><br>").slice(2);
  chatLog.innerHTML = messages;
}, 5000);
