# _Mates Rate_ Online Game

_Mates Rate_ is an online multiplayer game which lets you rate your friends and famous people in funny categories. The app updates in real time over websockets with Django Channels, and requests images using Google Custom Search API. The app is deployed on AWS with Elastic Beanstalk/RDS/ElastiCache/Route53. Front end is entirely vanilla JS and CSS, backend uses Django, Postgres and Redis.

Play now on https://matesrate.net/!

You'll need two friends as the game needs minimum three players. Or you can play around using different devices/Chrome profiles (the game uses cookies so you cannot play on multiple tabs). Or, just watch the opening animations to get an idea...

All design and artwork the author's own. Get in touch if you have deployment questions - it was a slightly painful process involving lots of fiddling with eb platform hooks!

## Design Choices

### 01: Why have all players broadcasting, not just the host?

There is lots of code in consumers.py concerned with managing multiple broadcasts, so having only the host manage broadcasting and the updating of game data might seem like an easy simplification. However, if the host were to disconnect from the game for a period of time (and thus be removed from the channel group), this might lead to missed messages and game errors. By having the most recent player to submit information lead the broadcast and process game logic, this kind of error should be much less likely.

### 02: Why not have a game class with methods instead of a bunch of util functions?

A game class containing all the util functions as methods would save a lot of repeated code in consumers.py as it would be unnessecary to pass self.game_id and other data to each util call. Some game data could also be cached saving code and db calls in the util functions themselves. However, due to issue 01 (see above), any player can update the game state, so multiple game classes would need to be upkept. This is a complication that for the time being I have chosen to avoid! Instead, the util functions are imagined as 'pure' in that they have no side effects apart from their interaction with the game db. This means that any player in any game can call these functions without inconcistencies arising.

### 03: Why broadcast at all?

To be honest - not totally sure! I was having errors early on in development that led me to think I might not be able to rely on messages being processed in order when internet connection is unstable. I decided a continuous broadcasting of game data would protect against this if it was indeed an issue. If something spooky does go wrong with an individual message, then it should be corrected on the next broadcast.

## To Do

### Refactoring

- Improve accessibility - go through lighthouse reports etc. Some missing labels on input fields in game etc.
- Think about the behaviour of skip round - doesn't achieve much at the moment. Also needs refactoring from its previous name of `force-next` in places.
- Improve SEO
- Could make better use of Django HTML templating
- Try to improve cohesion of consumers.py, delegate work elsewhere maybe.
- Use BEM in styles for readability

### Features

- add public game feature or play against the computer
- if websocket connection fails, try again and notify user that they are reconnecting
- include a measure of spread in results - highest and lowest score maybe?
