# Description
##### Custom Instagram feed sent over a telegram bot.

I've been wanting a feed of instagram bands posts to know when they play whitout having to look over each one of the bands I like, like haveing an _exclusive notification_ for these kind of posts. So I thoutgh that making a bot that would do just that would be a nice exerisce


## Use cases
I generalized the idea of live performances of bands to any kind of instagram account, and the idea of finding out whether or not the publication is a promotion for a perfomance as the search for certain custom keywords in the publication's caption. Then, this bot lets you choose what new posts of instagram accounts you are going to be feeded, given that those posts have your custom keywords.


## Implementation
The language used is python. The bot uses `telegram-python-bot`, but the tool itself to get new publications is independent from the bot, and uses the `selenium` module to get the posts. I'm currently using `sqlite` as the database engine to store all the pertinent information via `Pony ORM`.

## Updates and todos
For now I'm going to use the feeder as is, fixing bugs depending on their severity as I encounter them. I already have updates and todos planned for the future, some of them are:
- New functionalities:
  - Add functions to stop and resume the job that checks whether or not there are new posts
  - Add functions to get the last n posts, regardless of date
  - Process error messages, given by the feeder, to send through the bot in a more friendly user manner
  - Add OCR to search for the given keywords on the posts pictures also
- Bug fixes:
  - Fix date not found on posts error
- General upgrades:
  - Investigate alternative solutions to `selenium`


Feel free to ask me any questions or make any suggestions.
