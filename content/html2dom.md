Title: html2dom
Date: 2013-09-24
Slug: html2dom
Author: Frederik

I originally blogged about *html2dom* on the [Mozilla Security Blog](https://blog.mozilla.org/security/2013/09/24/introducing-html2dom-an-alternative-to-setting-innerhtml/)

Having spent significant time to [review the source code of some Firefox OS core apps](https://wiki.mozilla.org/Security/Reviews/Gaia), I noticed that a lot of developers like to use `innerHTML` (or `insertAdjacentHTML`). It is indeed a useful API to insert HTML from a given string without hand-crafting objects for each and every node you want to insert into the DOM.
The dilemma begins however, when this is not a hardcoded string but something which is constructed dynamically. If the string contains user input (or something from a malicious third-party - be it app or website), it may as well insert and change application logic (Cross-Site Scripting): The typical example would be a `&lt;script>` tag that runs code on the attacker's behalf and reads, modifies or forwards the current content to a third-party. [CSP](https://developer.mozilla.org/en/docs/Security/CSP "Content Security Policy"), which we use in Firefox OS, can only mitigate some of these attacks, but [certainly not all](http://lcamtuf.blogspot.de/2011/12/notes-about-post-xss-world.html).

#### Using innerHTML is bad (Hint: DOM XSS)

What's also frustrating about these pieces of code is that analyzing it requires you to manually trace every function call and variable back to its definition to see whether it is indeed tainted by user input.

With code changing frequently those reviews don't really scale. One possible approach is to avoid using `innerHTML` for good. Even though this idea sounds a bit naive, I have dived into the world of automated HTML parsing and code generation to see how feasible it is.

#### Enter html2dom

For the sake of experimentation (and solving this neatly self-contained problem), I have created [html2dom](https://github.com/freddyb/html2dom). html2dom is a tiny library that accepts a HTML string and returns alternative JavaScript source code. Example:
`<p id="greeting">Hello <b>World</b></p>`

Will yield this (as a string).

```js

var docFragment = document.createDocumentFragment();
// this fragment contains all DOM nodes
var greeting = document.createElement('P');
greeting.setAttribute("id", "greeting");
docFragment.appendChild(greeting);
var text = document.createTextNode("Hello ");
greeting.appendChild(text);
var b = document.createElement('B');
greeting.appendChild(b);
var text_0 = document.createTextNode("World");
b.appendChild(text_0);
```

As you can see, html2dom tries to use meaningful variable names to make the code readable. If you want, you can try the [demo here](http://freddyb.github.io/html2dom/). Now we could also just replace the `"World"` string with a JavaScript variable. It cannot do any harm as it is always rendered as text.

#### When it comes to HTML parsers, you _also_ don't want to write your own.

Luckily, there are numerous very useful APIs which helped making the development of html2dom fairly easy. First there is the [DOMParser API](https://developer.mozilla.org/en-US/docs/Web/API/DOMParser) which took care about all HTML parsing. Using the DOM tree output, I could just iterate over all nodes and their children to emit a specific piece of JavaScript depending on its type (e.g., HTML or Text). For this, the [nodeIterator](https://developer.mozilla.org/en-US/docs/DOM/Document.createNodeIterator) turned out really valuable.

I have also written a few [unit tests](http://freddyb.github.io/html2dom/tests/tests.html), so if you want to start messing with my code, I suggest you start by checking them out right away.

#### Known Bugs & Security

This tool doesn't really save you from all of your troubles. But if you can, make sure that the user input is always somewhere in a text node, then html2dom can prevent you from a great deal of harm. [Give it a try!](http://freddyb.github.io/html2dom/)

#### On the horizon

I have also been looking at attempts to rewrite potentially dangerous JavaScript automatically. This is at an early stage and still experimental but you can look at a [prototype](http://people.mozilla.com/%7Efbraun/falafler/) here
