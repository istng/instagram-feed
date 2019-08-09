# Description
##### Custom Instagram feed sent over a telegram bot.

I've been wanting a feed of instagram bands posts to know when they play whitout having to look over each one of the bands I like, like having an _exclusive notification_ for these kind of posts. So I thoutgh that making a bot that would do just that would be a nice exerisce


## Use cases
I generalized the idea of live performances of bands to any kind of instagram account, and the idea of finding out whether or not the publication is a promotion for a perfomance as the search for certain custom keywords in the publication's caption. Then, this bot lets you choose what new posts of instagram accounts you are going to be feeded, given that those posts have your custom keywords.

Alternatively, you can also receive all new posts from the accounts you want. And there is also a function to get any amount of lasts posts you would want from a given account.


## Implementation
The language used is python. The bot uses `telegram-python-bot`, but the tool itself to get new publications is independent from the bot, and uses the `instaloader` module to get the posts. I'm currently using `sqlite` as the database engine to store all the pertinent information via `Pony ORM`.

## Updates and todos
I'm going to be updating the bot now and again fixing bugs depending on their severity as I encounter them and making upgrades. I already have updates and todos planned for the future, some of them are:
- New functionalities:
  - Add functions to stop and resume the job that checks whether or not there are new posts
  - Process error messages, given by the feeder, to send through the bot in a more friendly user manner
  - Add OCR to search for the given keywords on the posts pictures also
- Bug fixes:
  - Fix date not found on posts error, patched but not fixed
  - Fix _page not found_ from instagram, patched but not fixed
- General upgrades:
  - Optimize the usage of `instaloader`


Feel free to ask me any questions or make any suggestions.
