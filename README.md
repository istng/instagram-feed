# Description
Custom Instagram feed sent over a telegram bot.

I've been wanting a feed of instagram bands posts to know when they play whitout having to look over each one of the bands I like, like haveing an _exclusive notification_ for these kind of posts. So I thoutgh that making a bot that would do just that would be a nice exerisce


# Use cases
I generalized the idea of live performances of bands to any kind of instagram account, and the idea of finding out whether or not the publication is a promotion for a perfomance as the search for certain custom keywords in the publication's caption. Then, this bot lets you choose what new posts of instagram accounts you are going to be feeded, given that those posts have your custom keywords.


# Implementation
The language used is python. The bot uses `telegram-python-bot`, but the tool itself to get new publications is independent from the bot, and uses the `selenium` module to get the posts. I'am currently using `sqlite` as the database engine to store all the pertinent information, via `Pony ORM`.

The project is currently being updated as I learn new techniques to solve the problems I find.
