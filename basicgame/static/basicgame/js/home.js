import { refreshPage } from "./base.js";

refreshPage();

const hostButton = document.getElementById("host-game");
const joinButton = document.getElementById("join-game");
const helpButton = document.getElementById("help-button");
const helpText = document.getElementById("help-text");
const spinner = document.getElementById("spinner");
const closeHelpButton = document.getElementById("close-help");
const title = document.querySelector("h1");
const subtitle = document.querySelector("h3");
const leftSpeech = document.querySelectorAll(".left-hints");
const rightSpeech = document.querySelectorAll(".right-hints");
const leftSpeechContent = document.getElementById("speech-left");
const rightSpeechContent = document.getElementById("speech-right");
const hintList = JSON.parse(document.getElementById("hint-list").textContent);
const categoryHints = JSON.parse(
  document.getElementById("category-hints").textContent
);
const characterHints = JSON.parse(
  document.getElementById("character-hints").textContent
);
const philosopher = document.getElementById("philosopher");

function hintsGenerator() {
  let hintCount = -1;
  let count = -1;
  function inner() {
    if (hintCount === hintList.length - 1 || count % 2 === 0) {
      count++;
      const randCharInt = Math.floor(Math.random() * characterHints.length);
      const char = characterHints[randCharInt].slice(0, -1);
      const randCatInt = Math.floor(Math.random() * categoryHints.length);
      const cat = categoryHints[randCatInt].slice(0, -1);
      return `How does ${char} score in the category of ${cat}?`;
    } else hintCount++;
    count++;
    return hintList[hintCount];
  }
  return inner;
}

function startHintsReel() {
  rightSpeech.forEach((element) => (element.style.display = "block"));
  leftSpeech.forEach((element) => (element.style.display = "block"));
  rightSpeechContent.style.display = "flex";
  leftSpeechContent.style.display = "flex";
  setTimeout(() => {
    rightSpeech.forEach((element) => (element.style.opacity = "90%"));
    leftSpeech.forEach((element) => (element.style.opacity = "0%"));
  }, 1000);

  const nextHint = hintsGenerator();
  let count = 0;

  function updateHints() {
    count++;
    leftSpeech.forEach((element) => (element.style.opacity = "0%"));
    rightSpeech.forEach((element) => (element.style.opacity = "0%"));
    setTimeout(() => {
      if (count % 2 === 0) {
        rightSpeechContent.innerHTML = nextHint();
        rightSpeech.forEach((element) => (element.style.opacity = "90%"));
      } else {
        leftSpeech.forEach((element) => (element.style.opacity = "90%"));
        leftSpeechContent.innerHTML = nextHint();
      }
    }, 1000);
  }
  const interval = setInterval(updateHints, 5000);
  return { updateHints, interval };
}

function showSpinner() {
  const elements = [
    helpText,
    hostButton,
    joinButton,
    helpButton,
    closeHelpButton,
    title,
    subtitle,
    ...rightSpeech,
    ...leftSpeech,
    philosopher,
  ];
  elements.forEach((element) => (element.style.display = "none"));
  spinner.style.height = "100px";
  spinner.style.width = "100px";
  spinner.style.display = "block";
}

hostButton.addEventListener("click", () => {
  window.location.pathname = "/host";
  showSpinner();
});

joinButton.addEventListener("click", () => {
  window.location.pathname = "/join";
  showSpinner();
});

helpButton.onclick = function (e) {
  helpText.style.display = "block";
};

closeHelpButton.onclick = function (e) {
  helpText.style.display = "none";
};

let { updateHints, interval } = startHintsReel();

philosopher.onclick = function (e) {
  clearInterval(interval);
  updateHints();
  interval = setInterval(updateHints, 5000);
};
