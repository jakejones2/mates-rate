import { getCookie } from "./base.js";

// game data

const gameName = JSON.parse(document.getElementById("game-name").textContent);
const playerName = getCookie(gameName)["playerName"];
const host = JSON.parse(document.getElementById("game-host").textContent);
const categoryHints = JSON.parse(
  document.getElementById("category-hints").textContent
);
const characterHints = JSON.parse(
  document.getElementById("character-hints").textContent
);
const players = JSON.parse(document.querySelector("#players").textContent);

// elements

const submit = document.querySelector("#game-submit");
const heading = document.getElementById("heading");
const input = document.getElementById("game-input");
const category = document.getElementById("category");
const character = document.getElementById("character");
const voteLabels = document.querySelectorAll(".vote-text, .vote-submit-text");
const forceNext = document.getElementById("force-next");
const table = document.querySelector("table");
const headingSmaller = document.querySelector("#heading-smaller");
const winnerText = document.querySelectorAll(".winner-text");
const scoreText = document.querySelector("#score");
const validator = document.querySelector("#validator");
const boringHeader = document.querySelector("#boring-header");
const boringCategory = document.querySelector("#boring-category");
const winningCharacter = document.querySelector("#winning-character");
const helpButton = document.getElementById("help-button");
const helpText = document.getElementById("help-text");
const closeHelpButton = document.getElementById("close-help");
const main = document.querySelector("main");
const speechBubble = document.getElementById("speech-bubble");
const speech = document.getElementById("speech");
const spinner = document.getElementById("spinner");
const allElements = document.getElementById("desktop-center");
const body = document.querySelector("body");
const leave = document.getElementById("leave");
const closeLeave = document.getElementById("close-leave");
const yesLeave = document.getElementById("yes-leave");
const winnerImage = document.getElementById("winner-image");
const timer = document.getElementById("timer");
const gameNameFooter = document.getElementById("game-name-footer");

// vars
let websocketAddress;
if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
  websocketAddress =
    "ws://" + window.location.host + "/ws/" + gameName + "/play/";
} else {
  websocketAddress =
    "wss://" + window.location.host + "/wss/" + gameName + "/play/";
}
const gameSocket = new WebSocket(websocketAddress);

let view = null;
let sending = null;
let hintsReel = null;
let currentRound = "Round 1";

// utils - css

function hideElements() {
  const elements = [
    heading,
    headingSmaller,
    input,
    submit,
    category,
    character,
    forceNext,
    table,
    scoreText,
    validator,
    boringHeader,
    boringCategory,
    winningCharacter,
    speechBubble,
    speech,
    winnerImage,
    timer,
    ...voteLabels,
    ...winnerText,
  ];
  for (const element of elements) {
    element.style.display = "none";
  }
}

function showElements(elements) {
  hideElements();
  for (const element of elements) {
    if (element === forceNext) {
      if (host === playerName) {
        submit.style.marginBottom = "1em";
        forceNext.style.display = "block";
      }
    } else if (element === table) {
      table.style.display = "table";
    } else {
      element.style.display = "block";
    }
  }
}

function centerElements() {
  main.style.position = "absolute";
  main.style.top = "40%";
  main.style.left = 0;
  main.style.right = 0;
  main.style.margin = "auto";
  main.style.transform = "translate(0, -40%)";
}

function topAlignElements() {
  if (window.innerWidth >= 768) return;
  main.style.position = "static";
  main.style.transform = "none";
  if (window.innerWidth < 768) {
    heading.style.marginBottom = "10%";
  }
}

function deBold(text) {
  return `<span style="font-weight: 500">${text}</span>`;
}

function hyphenate(text) {
  if (window.innerWidth >= 768) return text;
  const words = text.split(" ");
  const hyphenatedWords = words.map((word) => {
    if (word.length >= 15) {
      const end = word.slice(13);
      const start = word.slice(0, 13);
      return start + "-" + end;
    } else return word;
  });
  return hyphenatedWords.join(" ");
}

function highlightColor(element, color = "rgb(32, 214, 0)") {
  element.style.color = color;
  setTimeout((_) => (element.style.color = "black"), 1500);
}

function normalizeCss() {
  headingSmaller.style.color = "rgb(1, 15, 28)";
  headingSmaller.style.textShadow = "none";
  category.style.marginBottom = "1em";
}

function validate(message) {
  setTimeout(function () {
    validator.innerHTML = message;
    validator.style.display = "block";
    document.body.scrollTo({ top: document.body.scrollHeight });
    window.scrollTo(0, document.body.scrollHeight);
    setTimeout(function () {
      validator.style.display = "none";
    }, 2000);
  }, 100);
}

function hintsGenerator(list) {
  const max = list.length - 1;
  function inner() {
    const randInt = Math.floor(Math.random() * max);
    return list[randInt].slice(0, -1) + "?";
  }
  return inner;
}

function startHintsReel(list) {
  speechBubble.style.display = "block";
  speech.style.display = "flex";
  const nextHint = hintsGenerator(list);

  speech.innerHTML = nextHint();
  setTimeout(() => {
    speechBubble.style.opacity = "90%";
    speech.style.opacity = "90%";
  }, 1000);

  function updateHints() {
    speechBubble.style.opacity = "0%";
    speech.style.opacity = "0%";
    setTimeout(() => {
      speech.innerHTML = nextHint();
      speechBubble.style.opacity = "90%";
      speech.style.opacity = "90%";
    }, 1000);
  }
  hintsReel = setInterval(updateHints, 7000);
}

function resetTimerWheel(timeSeconds) {
  if (!timeSeconds) return;
  const duration = (timeSeconds - Date.now() / 1000).toFixed(1);
  timer.style.animation = "none";
  timer.style.animation = "";
  void timer.offsetWidth;
  timer.style.animation = `rotateAndFill ${duration}s linear`;
}

// utils - broadcasting

function gameSend(data) {
  gameSocket.send(JSON.stringify(data));
}

function broadcastAndWait(message = "Waiting for other players...", sendData) {
  showElements([headingSmaller, forceNext]);
  centerElements();
  headingSmaller.innerHTML = message;
  if (sendData) {
    sendData.sender = playerName;
    gameSend(sendData);
    sending = setInterval(gameSend, 3000, sendData);
  }
}

// utils - game views

function showSkipRoundView() {
  normalizeCss();
  centerElements();
  showElements([headingSmaller]);
  headingSmaller.innerHTML = "Round skipped by host...";
}

function showFinishView() {
  if (players.length < 5) centerElements();
  showElements([heading, table]);
  heading.innerHTML = "GAME OVER!";
  category.innerHTML = "Final scores:";
  setTimeout(function () {
    window.location.pathname = "/";
  }, 15000);
}

function showLeaderboardView(leaderboardHtmlTable) {
  if (players.length < 7) centerElements();
  normalizeCss();
  showElements([table, headingSmaller, forceNext, timer]);
  headingSmaller.innerHTML = "Leaderboard";
  table.innerHTML = leaderboardHtmlTable;
}

function showResultsView(resultsHtmlTable) {
  if (players.length < 7) centerElements();
  showElements([heading, table, forceNext, timer]);
  heading.innerHTML = "Results";
  table.innerHTML = resultsHtmlTable;
}

function showWinnerView(
  isDraw,
  drawersList,
  winner,
  characterData,
  categoryData,
  score,
  imageUrl
) {
  topAlignElements();
  headingSmaller.style.color = "gold";
  headingSmaller.style.textShadow = "0 0 8px black";
  if (isDraw) {
    showElements([headingSmaller, forceNext, timer]);
    headingSmaller.innerHTML = `Draw between ${drawersList.join(" and ")}`;
  } else {
    winnerImage.src = imageUrl;
    showElements([
      headingSmaller,
      ...winnerText,
      category,
      winningCharacter,
      scoreText,
      forceNext,
      winnerImage,
      timer,
    ]);
    if (!winnerImage.src) winnerImage.style.display = "none";
    headingSmaller.innerHTML = `${winner} wins!`;
    winningCharacter.innerHTML = `${characterData}`;
    category.innerHTML = categoryData;
    scoreText.innerHTML = score;
  }
}

function showVoteView(categoryText, poll) {
  topAlignElements();
  showElements([
    heading,
    input,
    submit,
    category,
    character,
    ...voteLabels,
    forceNext,
  ]);
  heading.innerHTML = "Vote!";
  input.value = "";
  category.innerHTML = categoryText;
  character.innerHTML = poll[0];
  const voteData = { category: categoryText, characterScores: {} };
  let n = 0;
  submit.onclick = function (e) {
    validator.style.display = "none";
    if (+input.value >= 0 && +input.value <= 100 && input.value != "") {
      voteData.characterScores[poll[n]] = input.value;
      n += 1;
      character.innerHTML = poll[n] ? poll[n] : "";
      input.value = "";
      window.scrollTo(0, 0);
      document.body.scrollTo({ top: 0 });
      highlightColor(character);
      if (n === poll.length) {
        const sendData = {
          vote: { name: playerName, voteData: voteData },
        };
        broadcastAndWait("Waiting for other players...", sendData);
      }
    } else {
      highlightColor(input, "crimson");
      validate("Enter a number between 0 and 100...");
    }
  };
}

function showCharacterView(categoryPicker, categoryText) {
  centerElements();
  if (playerName === categoryPicker) {
    broadcastAndWait("Waiting for characters...");
  } else {
    showElements([
      boringHeader,
      boringCategory,
      input,
      submit,
      forceNext,
      heading,
      speech,
      speechBubble,
    ]);
    startHintsReel(characterHints);
    boringCategory.innerHTML = categoryText;
    heading.innerHTML = "Enter a character:";
    submit.onclick = function (e) {
      if (input.value.length < 1) {
        validate("Enter a longer character...");
      } else {
        const characterText = hyphenate(input.value);
        const sendData = {
          submission: { name: playerName, text: characterText },
        };
        broadcastAndWait("Waiting for server", sendData);
      }
    };
  }
}

function showSubmissionView(view) {
  clearInterval(hintsReel);
  centerElements();
  normalizeCss();
  showElements([heading, input, submit, forceNext, speech, speechBubble]);
  // boring mode
  if (view.startsWith("boring_")) {
    const leadPlayer = view.slice(7);
    if (playerName === leadPlayer) {
      startHintsReel(categoryHints);
      heading.innerHTML = "Enter a category:";
      submit.onclick = function (e) {
        if (input.value.length < 1) validate("Enter a longer category...");
        else if (input.value.length > 100) {
          validate("Enter a shorter category...");
        } else {
          const categoryText = hyphenate(input.value);
          const sendData = {
            category: { name: playerName, text: `_${categoryText}` },
          };
          broadcastAndWait("Waiting for server...", sendData);
        }
      };
    } else {
      broadcastAndWait(
        `${deBold("Waiting for")}<br>${leadPlayer.slice(0, -8)}<br>${deBold(
          "to offer a category..."
        )}`
      );
    }
  }
  // normal mode
  else {
    if (playerName === view) {
      startHintsReel(categoryHints);
      heading.innerHTML = "Enter a category:";
      submit.onclick = function (e) {
        if (input.value.length < 1) validate("Enter a longer category...");
        else if (input.value.length > 100) {
          validate("Enter a shorter category...");
        } else {
          const categoryText = hyphenate(input.value);
          const sendData = {
            submission: { name: playerName, text: `_${categoryText}` },
          };
          broadcastAndWait("Waiting for other players...", sendData);
        }
      };
    } else {
      startHintsReel(characterHints);
      heading.innerHTML = "Enter a character:";
      submit.onclick = function (e) {
        if (input.value.length < 1) {
          validate("Enter a longer character...");
        } else {
          const characterText = hyphenate(input.value);
          const sendData = {
            submission: { name: playerName, text: characterText },
          };
          broadcastAndWait("Waiting for other players...", sendData);
        }
      };
    }
  }
}

// websocket receiver - coordinates views

gameSocket.onmessage = function (e) {
  spinner.style.display = "none";
  allElements.style.display = "block";
  const data = JSON.parse(e.data);
  if (view === data.view) return;
  if (sending) clearInterval(sending);
  resetTimerWheel(data.nextViewAt);
  view = data.view;
  switch (view) {
    case "skip":
      showSkipRoundView();
      break;
    case "finish":
      showFinishView();
      break;
    case "leaderboard":
      showLeaderboardView(data.leaderboardHtmlTable);
      break;
    case "results":
      showResultsView(data.resultsHtmlTable);
      break;
    case "winner":
      showWinnerView(
        data.winner["is_draw"],
        data.winner["drawers_list"],
        data.winner.name,
        data.winner.character,
        data.winner.category,
        data.winner.score,
        data.image
      );
      break;
    case "vote":
      showVoteView(data.category, data.poll);
      break;
    case "character":
      showCharacterView(data.categoryPicker, data.category);
      break;
    default:
      showSubmissionView(view);
      currentRound = data.round;
      break;
  }
};

// UI

if (!players.includes(playerName)) {
  alert("You are not a member of this game and cannot partake! GO AWAY!");
}

if (window.innerWidth >= 768 && playerName === host) {
  body.appendChild(forceNext);
  if (allElements.contains(forceNext)) {
    allElements.removeChild(forceNext);
  }
}

gameSocket.onclose = () => {
  setTimeout(() => {
    location.reload(true);
  }, 500);
};

input.onkeyup = function (e) {
  if (e.keyCode === 13) {
    submit.click();
  }
};

forceNext.addEventListener("click", () => {
  spinner.style.display = "block";
  allElements.style.display = "none";
  gameSend({ force_next: "_" });
});

helpButton.addEventListener("click", () => {
  helpText.style.display = "block";
});

closeHelpButton.addEventListener("click", () => {
  helpText.style.display = "none";
});

// modal

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

// show the help menu upon opening

helpText.style.opacity = 0;
helpText.style.display = "block";

setTimeout(() => {
  helpText.style.animation = "fade-in";
  helpText.style.animationDuration = "1s";
  helpText.style.animationFillMode = "forwards";
  setTimeout(() => {
    helpText.style.opacity = 1;
    helpText.style.animation = "disappear-into-corner";
    helpText.style.animationDuration = "1s";
    helpText.style.animationFillMode = "none";
    setTimeout(() => {
      helpButton.style.animation = "flash";
      helpButton.style.animationDuration = "2s";
      helpText.style.display = "none";
      helpText.style.animation = "none";
    }, 900);
  }, 3000);
}, 1000);

// alternate footers

let footerCount = 0;
setInterval(() => {
  footerCount++;
  if (footerCount % 2 !== 0) {
    gameNameFooter.innerHTML = currentRound;
  } else {
    gameNameFooter.innerHTML = `Game ID: ${gameName}`;
  }
}, 3000);
