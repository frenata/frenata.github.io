% Android Architecture, Part 1
% 
% 15 April 2017

Frustrated by communication issues while working on my WGU capstone/thesis, I recently turned to the only other class I have left: Mobile Application Development. I was fairly excited by this (I get to build Android apps!), but the reality of the class was somewhat intimidating. There is no objective assessment, only a performance assessment that involves building an actual app. Fine. But provided materials are...minimal. No problem, I thought, since android development is so popular there should be plenty of information freely available on the web!

While my original plan was to work through some of Udacity's free material on Android, then to launch into the class project, I realized that the time left in my term was quickly running out. Not having time to learn it "the right way", I resolved to "fake it until I made it," passing the class, and revisiting android development proper when my time permits. My first step was to follow a tutorial to build a working app along similar lines to what I needed to eventually build. I pulled from two tutorials to get the basics rolling:

* Lynda's [Note-Taking App](https://www.lynda.com/Android-tutorials/Building-Note-Taking-App-Android/377485-2.html) video tutorial, which was specifically linked on the WGU course page
* Vogella's [Android SQLite database tutorial](http://www.vogella.com/tutorials/AndroidSQLite/article.html), which is just text and lots of code samples, covering a variety of ways to interact with a SQLite database in Android

I primarily followed the Lynda tutorials, adjusting and learning as I went. For instance, that tutorial uses a very simple DB table with just two columns: the text of the note and the id (primary key) of the note. For even the simplest of my tables I needed to store at least 4 pieces of information: a term title, start and end dates, and the id. Thus my app quickly diverged from the tutorial, with multiple relevant fields complicating the layout files. To list data, android provides some basic list layouts, but they hold only up to two pieces of info. Since I wanted to dispaly three pieces of information, I had to build my own custom list layout.

I kept the basic class structure the same, although looking forward somewhat I seperated my `TermTable`, representing a single SQL table, from my `SchedulerDBHelper`, which opens/creates/upgrades the database itself, and my `SchedulerProvider`, which is a ContentProvider to allow "easy" access to the database. Early on, I also implemented a separate `Term` class to handle bundling of the values from the `TermTable` table, but I later merged these together into a single class called `Term`, to handle all things related to a "term".

From that point on, working through the rest of the tutorials was relatively straightforward, until I had a working app that let me display lists of terms and edit them, all backed by a SQLite database. But of course, this was only the beginning.
