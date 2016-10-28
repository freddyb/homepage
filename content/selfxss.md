Title: (Self) XSS at Mozilla's internal Phonebook
Date: 2014-05-23
Slug: self-xss
Author: Frederik

This is a short summary about a goofy XSS/CSRF exploit on an internal
web page at Mozilla.

A few weeks ago I discovered that our "phonebook" supports a limited
wiki-syntax in the profile descriptions (i.e. `[link text http://example.com]`). Despite proper sanitizing to
forbid all markup injections into HTML tags and attributes it allowed
linking to `javascript` URLs. Liking the rich capabilities that come with
JavaScript, I naturally had to insert some script into my profile.
So I started with a small script that changes the background color randomly.
Like this:

[Click me, I dare you](javascript:void%28setInterval%28%22document.body.style.backgroundColor%3D%27%23%27+%28Math.random%28%29*10e16%29.toString%2816%29.substr%280%2C6%29%22%2C500%29%29)

Source:

```js
void(setInterval("document.body.style.backgroundColor='#'+(Math.random()*10e16).toString(16).substr(0,6)",500))
```

What it does? Well, let's start simple. `setInterval(…,500)` runs the
code supplied in the first argument every 500ms. The code itself is an
assignment to the document's background color. So we change it quite often.
The rest is a quick way to generate a random six digits hex string, i.e.
an RGB color value: `Math.random()` gives a float with a lot of random
digits after the floating point. Multiplying by 10e16 (that is a 10
followed by 16 zeros) makes it a long integer without decimals. `toString(16)`
transforms it into a hex string and `substr` cuts after six digits. Et violà!
`void` makes sure the code doesn't have a return value, which means that
the browser stays on the current web page. I have manually shortened
the code to work without spaces, so it does not break the wiki-syntax.

Well that was the first revision. I left it for a while and I guess people
clicked on it. I don't know how many, but surely somebody found it.
That was part one. I came back to this a few weeks later and had to
realize that changing the background color is quite boring. What else can
we do? Right. We can try to change other people's profiles.

This is where the fun starts:[^1]

```js
javascript:i=document.createElement("iframe");i.src="edit.php";i.style.display="none";document.body.appendChild(i);void(setTimeout('f=(i.contentDocument.forms[0\x5D);f[atob("bmFtZVtd")\x5D.value+="\x20\uD83D\uDC35";f.submit()',20e2))
```

Again, this link came with the same "I dare you" text. Let's dissect the source
code. First we create an invisible iframe that loads the "Edit Profile" page.

```js
i=document.createElement("iframe");
i.src="edit.php";
i.style.display="none";
document.body.appendChild(i);
```

Now let's fill out the form and submit. The frame takes some time to load,
so we will prepare a piece of source code in a string and defer execution
with `setTimeout`: The code finds the form in the iframe, DOM navigation
is quite easy since the input fields have proper `name` attributes, which
exposes them to JavaScript as attributes of the form element.
The source code uses `atob`, `\x5D` and `\x20` so we don't break wiki-syntax.
The escape sequence `\uD83D\uDC35` is the unicode monkey face 🐵.


```js
payload = 'f=(i.contentDocument.forms[0\x5D);f[atob("bmFtZVtd")\x5D.value+="\x20\uD83D\uDC35";f.submit()'
```

Once the payload is prepared we just execute it after a certain delay:

```js
void(setTimeout(payload,20e2))
```

So to recap: If you click this link you will add a monkey face to your name
in the background, but it's quite subtle.

So let's search for the monkey face in the phonebook:
![Search results](/images//selfxss-results.png)

At least 12 people have a monkey in their profile 🐵[^2]

This isn't strictly a self-xss as discussed in these three very interesting
blog posts ([1](http://incompleteness.me/blog/2011/12/14/combating-self-xss/),
[2](http://inpursuitoflaziness.blogspot.in/2014/04/the-battle-against-self-xss.html),
[3](http://incompleteness.me/blog/2014/04/24/combatting-self-xss-part-2/))
but I'd argue that the average Mozillian should be careful enough *not*
to click links that start with `javascript:` ;)



[^1]: I have modified a few bits so the exploit doesn't properly apply to
the phonebook. Script kiddie protection.

[^2]: I swear it was only 11 when I started writing this blog post. Also,
modulo a false positive: One person had a monkey in their description before
I started this.


