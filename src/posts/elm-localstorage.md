% Saving a partial Elm Model to LocalStorage
% Andrew Nichols
% 9 September 2017

### Pollution
I was nearly finished building a relatively simple webapp to [simulate stock trading](https://github.com/frenata/stocksim), when a problem I had set aside from the beginning of the work came looming back: storing the data.

The app gives you some money to play with and allows you to buy and sell stocks, but the portfolio data was purely ephemeral, vanishing with a refreshed page. That doesn't make much sense for a simulation that would most likely be used over a number of days.

But I had set the issue aside in favor of building out the actual features, knowing that eventually I would have to get my hands dirty in the world of Elm "ports", a feature that allows non-functional JS code to interop with the clean and pure Elm code.

### Copypasta
A little [research](http://lmgtfy.com/?q=elm+localstorage) turned up some useful information, including a lovely tutorial on building Elm apps that included detailed instructions on how to setup ports for localStorage.

Hurrah!

There wasn't much to implement, and it mostly made sense.

* a few extra lines of JS in my index.html, to
	* initialize the Elm app with the stored model
	* save the model to storage
	* remove the model from storage
* some `port` declarations in Elm
* a helper function with this type: `Model -> ( Model, Cmd Msg )` that needed to be inserted into the `update` function, capturing certain model updates to create the side effect of the JS interop

The last one was the weirdest to wrap my head around, but the entire effort was promisingly easy.

### Friendship is Magic
As is typical of making changes to an Elm program, compiling resulted in a friendly error message.

```
Port `setStorage` is trying to communicate an unsupported type.

352| port setStorage : Model -> Cmd msg
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The specific unsupported type is:

	Dict.Dict String { name : String, shares : Int, price : Float }

The types of values that can flow through in and out of Elm include:

	Ints, Floats, Bools, Strings, Maybes, Lists, Arrays, Tuples, Json.Values,
	and concrete records.
```

This was a problem. My data model did use a `Dict` to store stock positions in a user's portfolio, but apparently Elm wasn't having that.

I poked around to see if I could modify the code I'd only half-understood to send/recieve something other than the whole model. The good news: yes. The bad news: the data I actually cared about storing was that `Dict`.

### Life Finds a Way
After a few half starts and many more friendly error messages, I started to put together a solution. The `Dict` library helpfully included the pair of functions `toList` and `fromList`, which according to the compiler *were* eligible for sending via ports.

On examination, the only data that needed to be kept was the cash balance and the list of positions, so the concrete data type that ended up being sent/recieved was:

`(Float, List (String, Position))`

Position is a concrete record type with a couple of pieces of relevant data. Probably there's still some useful refactoring to be done here by aliasing the above tuple to a named type, since it shows up in several places.

### Failure is Victory
Only a smattering more work remained after this insight. My `init` function needed to rebuild the floating balance and the dictionary, leaving it with this ugly type signature:

`init : Maybe ( Float, List ( String, Position ) ) -> ( Model, Cmd Msg )`

It's all I can do to *not* go create a SavedPortfolio type alias right now.

I also updated the JS to provide a better key name to the saved data: "portfolio" rather than "model". That led me on a crazy bughunt that only ended when I realized I had changed the key value only in the function calls to save and remove... but not to initialize the Elm app. Put that in the "literals should be defined as constants" file.

The actual code for stock trading is not very interesting, but delving into using localStorage and ports ended up forcing me to learn a bunch. I consider myself fortunate that my use case was *just* different enough from the tutorial code as to not work at all. If my model had been "sendable" in the first place, the code would have worked, I would have been satisfied, but I would have walked away without much actual knowledge of *how* it worked.

tl;dr: Failing is learning.
