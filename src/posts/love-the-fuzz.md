% How I learned to stop worrying and love the fuzz
% Andrew Nichols
% 3 October 2017

#### The Mystery

Fuzzing has always been shrouded in mystery to me. Throwing random data at your program and seeing how it reacts felt like something for better programmers or more industrial applications, not the relatively small things I find myself more likely to write.

This week I dipped my toes into the mysterious waters of fuzzing, stopped worrying, and learned to love what fuzzing can do: reveal bugs in even small applications.

#### Unit Tests

Most working programmers will be familiar with the concept of testing their software, since it is unheard of for a non-trivial program to work right the first time. Unit testing generally refers to testing the smallest chunks of code for correctness before moving on to testing how those chunks work together.

An extreme form of this is the discipline of TDD or Test Driven Design, where the writing of a test that fails must always preceed the writing of working code that makes the test pass.

These practices are particularly great for getting working code done quickly and fearlessly improving the code later. Unfortunately, unit testing and TDD depend on something more fragile: the limits of a programmer's imagination about what could fail.

#### Imagine there's no errors/It's easy if you try

My imagination at least is sadly limited. Whether born of limited understanding of the material in question, wishful thinking, or laziness, it's easy to fail to imagine some particular way that my code can fail. I can test that certain expected inputs produce expected outputs, but what about unexpected inputs? Partially valid inputs? Malicious inputs?

In comes fuzzing, which makes no attempt to exhaustively test, but randomly tests various inputs.

Enlightenment came upon me while working on improving the code for my solution to the first [Cryptopals](https://www.cryptopals.com/) challenge. The challenge proposed the creation of a function that translated from hex encoding, where each character represents 4 bits, to [base64](https://en.wikipedia.org/wiki/Base64) encoding, where each character represents 6 bits. I pushed further, wanting to be able to easily change text between hex, base64, and ascii (character=8 bits) encodings. 

Because the number of bits encoded in a character are different between the three encodings, there isn't always a clean translation. I kept running into bugs that I had not imagined, fixing them, and running into more bugs. I finally had all my test cases passing, but had I really solved all the bugs? Or I had just solved the ones covered by my test cases?

#### The Bomb

Looking at my testing framework, I saw that it exposed a very simple way to create fuzz tests, and that the nature of the problem I was having was well adapted to testing with random input. The two core functions I was writing were `Base64.fromAscii` and `Base64.toAscii`: by the very nature of translating between encodings, any kind of ascii text passed first to the one and then to the other should be unchanged.

```
	\rand ->
	    rand
		|> Base64.fromAscii
		|> Base64.toAscii
		|> Expect.equal rand
```

This is the anonymous function which actually performs the work of my fuzz test. A random string named `rand` is passed through a series of pipes: it is translated from ASCII to Base64, then that new value is translated back into ASCII, then that new value is compared to the original random string.

Running this test 100 times immediately revealed errors in the translation functions that I had indeed not imagined. A common early failure:

```
Given "\n"

       ▼▼ 
    "\n\0"
    ╷
    │ Expect.equal
    ╵
    "\n"
```

In this case very short strings helped reveal the true nub of the problem I was having. Reencoded back to ASCII from base64, phantom null characters were being added on. To actually solve the problem I threw a few `Debug.log`'s into my code to inspect the text as it was being translated, narrowing down the issue. It turned out that since the character '\n' is really the number 10, that when it was encoded to hex it was represented as "a", but my ASCII encoder was processing hex characters in sets of 2.

#### Always forward

Not all problems are going to be as simple to apply this style of fuzzing to, since often we want controlled randomness. Just a little down the road in Cryptopals is a set of problems involving encrypting English texts against repeating keys, and then decrypting those same texts without the key. Throwing random data at the problem will not help, since the functions are specifically searching for the shape of normal-looking English text.

But we can shape random text, with more sophisticated fuzzers. My early notion is to drop a fairly large English textual source (Shakespeare, for instance) into my test directory, generate a random start position, and feed the indicated chunk of the text into the encryption algorithm along with a random key. On each run of the fuzzer, the original random key should be decrypted from the ciphertext.

No doubt there will be complications along the way. 

I started my base64 module with just a few unit tests, one that checks a specific ASCII string against its base64 encoding, and another which checks a specific hex string against its base64 encoding. Both remain to bear witness that I'm actually encoding to the proper representation. 

Beyond that, I see no need to write out a bunch of test cases with unusual input against their expected output, since if the fuzzer operates correctly, they will be identified anyway. Even better, I don't have to guess, imagine, or exhaustively list out test cases. I only have to love the fuzz.
