export function getCookie(name) {
  const key = name + "=";
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieList = decodedCookie.split(";");
  for (let cookie of cookieList) {
    cookie = cookie.trim();
    if (cookie.indexOf(key) === 0) {
      return {
        cookie: cookie,
        playerName: cookie.substring(key.length, cookie.length),
      };
    }
  }
  return { cookie: "", playerName: "" };
}

export function makeID(length) {
  let result = "";
  const characters =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  const charactersLength = characters.length;
  let counter = 0;
  while (counter < length) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
    counter += 1;
  }
  return result;
}

export function refreshPage() {
  window.onpageshow = function (event) {
    if (event.persisted) {
      window.location.reload();
    }
  };
}

export function addExpiration(cookieString) {
  const now = new Date();
  let time = now.getTime();
  time += 3 * 3600 * 1000;
  now.setTime(time);
  return cookieString + "; expires=" + now.toUTCString() + "; path=/";
}
