Title: Teacher's Pinboard Write-up
Date: 2015-12-02
Slug: teachers-pinboard-hack-lu-2015
Author: Frederik

> I found the address of the [teacher's pinboard](https://school.fluxfingers.net:1502/)!
> Can you try to get in and read all teachers' notes?
> Maybe you need to attack the admin account as well.

The [fluxfingers](http://fluxfingers.net/) (again) hosted the Capture The Flag (CTF) event for the [hack.lu security conference](https://hack.lu) in Luxembourg. It's long since I've left the university but I'm still fond of both the hack.lu CTF and fluxfingers, so I contributed two tasks for the event.

Since nobody bothered to publish their solution for the challenge, I have decided to release my own. By the way, you can still [access the challenge in the archive](https://school.fluxfingers.net:1502/) and I recommend you take a look yourself, before you continue reading this spoiler.

![screenshot](/images/teacher-pinboard-screenshot.png)


The teacher's pinboard is a website that provides you a log-in form that accepts any kind of username and password combination. After logging in, you are provided with a typical pinboard and you might notice that the website has provided you three cookies of the following format:

```text
session=7341e6fa2ab3b37f26e0cac6fedc25f3438e5fb9b12a9daed890459aa21f349b12676b3d;
accountinfo=(dp0%0AS'username'%0Ap1%0AS'foo'%0Ap2%0AsS'password'%0Ap3%0AS'bar'%0Ap4%0AsS'admin'%0Ap5%0AI00%0As.;
signature=81a380499ae8a9801c1b791da88d93bb5c74224ce59c60ae4a5010bc943ad85f
```

The accountinfo looks interesting!

Lets decode it:

```text
(dp0\nS'username'\np1\nS'foo'\np2\nsS'password'\np3\nS'bar'\np4\nsS'admin'\np5\nI00\ns.
```

With some research (or experience), one might notice that this is the output of [Python's pickle module](https://docs.python.org/2/library/pickle.html). Unpickling this thus leads the following dictionary:

```js
{'admin': False, 'password': 'bar', 'username': 'foo'}
```
Setting `admin` to `True` does not work, as the other cookie (`signature`) seems to enforce integrity of the `accountinfo` data. Another idea would be to attempt generic pickle exploits (like [so](https://blog.nelhage.com/2011/03/exploiting-pickle/)), which did not work out as well.
 
After some further close inspection, the user might notice that the JavaScript that comes with the pinboard does not only provide the nice user interface for playing with the notes. It also deals with the cookies! First it reads the cleartext password in your cookies and uses that to derive an encryption key. This key is then used to store the current notes in localStorage. Why? Mostly decoy, actually.

The interesting part is how it looks a the cookies. It does so by executing `pickle.loads()` in JavaScript.

"Pickle in JavaScript??" you say. Yes, in JavaScript. For this challenge, I have re-implemented Python's pickle module in JavaScript. Pickle is not actually a storage format but a nice little stack machine, that is easy to understand and fun to read. Take a look at `/usr/lib/python2.7/pickle.py` for example. The [JavaScript pickle code](https://school.fluxfingers.net:1502/javascripts/pickle.js) is worth a read too, but the concept is generally the same: If you want to execute a function, you load a reference to a global on the stack and call it using `R` (reduce). Parameters of said function should be a tuple on the stack just below the function.

So what would we do in JavaScript, if we wanted to execute arbitrary code but not write a pickle thing by hand? Well, throw our source code on the stack and call `eval()` of course. Turns out, the pickle.js author (me) thought of that too and implemented a blacklist, that disallows certain things:
```js
  const BLACKLIST = ["require", "eval", "setTimeout", "setInterval", "setImmediate"];
```

So that still leaves us with the `Function` constructor. I also know that Teams who solved this challenge used `process.mainModule.require`, which should also work. In general, the blacklist was more of a hint that one was going in the right direction than a real blocker.

I ended up writing a *compiler* that takes JavaScript source code and produces a pickle object that executes said code:

```js
function compiler(s) {
  // c= load global "Function" on stack
  // ( = set marker on stack, S = create String
  // t = create tuple from marker to top of stack
  //     (i.e. put string in a tuple)
  // R = call top-of-stack - 1 with top-of-stack as the argument
  //
  // i.e., call Function(), with s as param  
  var pickle = "cglobal\nFunction\n(S'"+s+"'\ntR";
  pickle +=    "(tR."
  return pickle;
};
```

Executing arbitrary code means you can now go through the directory and either find the file with the flag or find the source code and the secret key to produce an HMAC for a cookie that has `admin` set to `True`.
