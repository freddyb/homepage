<style>
h1,h2,h3,p,ol,ul { font-family: sans; }
blockquote { color: grey; }
</style>
# Remote Code Execution in Firefox beyond memory corruptions
## a comedy in five acts
>  *Browsers are complicated enough to provide attack surface beyond memory safety issues. This talk will look into injection flaws in the user interface of Mozilla Firefox, which is implemented in JS, HTML and an XML-dialect called XUL. Having achieved an XSS in the user interface, attackers can execute arbitrary code in the context of the browser application process (unsandboxed), with cross-platform exploits of high reliability. This talk discusses fixed browser vulnerabilities from 2017 and early 2018.*


# 0. Prologue
(This is the part, where we reduce the lighting and shine a flashlight into my face)
*Listen, well, young folks. Old people, browser hackers or Mozilla fanboys, might use this as an opportunity to lean back and stroke their mighty neckbeard, as they have heard all of this before*

It was the year 1997, and people thought XML was a great idea. In fact, it was so much better than its warty and unparseable predecessor HTML. While XHTML was the clear winner and successor for great web applications, it was *obvious* that XML would makee a great user interface markup language to create a powerful cross-platform toolkit dialect.
This folly marks the hour of birth for XUL. XUL was created as the *XML User Interface Language* at Netscape (the company that created the origins of the Mozilla source code. Long story. The younger folks might want to read upon Wikipedia or watch the amazing Movie "Code Rush", which is available on archive.org). Jokingly, XUL was also a reference to the classic 1984 movie Ghostbusters, in which an evil deity called Zuul (with a Z) possesses innocent women.

Time went by and many smart people realized that XUL did not take off as a widely-recognized standard for cross-platform user intefaces. Shocking, right? Many parts of the Firefox have thus been moving away from XUL and are thus implemented in HTML.
Aptly named after an evil spirit, we will see that XUL still haunts us today.

# Act 1, Scene 1 Mapping the attack surface
Let's look into Firefox, to find some remnants of XUL, by visiting some internal pages. Let's take a look at `about:downloads`. We can see that it lists all previously downloaded files.

We can open the source code with built-in the Web Developer Tools (e.g., Tools->Web Developer->Page Source). The heretics among you might want to download Firefox first or [use Firefox code search at searchfox.org](https://searchfox.org/mozilla-central/rev/8e8ccec700159dc4efe061cfec2af10b21a8e62a/browser/components/downloads/content/contentAreaDownloadsView.xul). We can also open the developer console and poke around with the obscure objects and functions that are available for JavaScript in privileged pages. As a proof-of-concept, we may `alert(Components.stack)`, which gives us a stringified JavaScript call stack but is left undefined for normal web content.

Inspecting the source code we can already see some markup that screams both *XML* as well as *XML-dialect*. While still in our information gathering face, we will not go too deep, but make note of two observations:
- XUL is not HTML. To get a better understanding of elements like `<command>`, `<colorpicker>` or `<toolbar>`, we will be able to look at the [XUL Reference on MDN](https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XUL/XUL_Reference)
- XUL is scriptable! A `<script>` tag exists and it may contain JavaScript.

There are also some newer pages like `about:crashes`, which holds previously submitted (or unsubmitted) crash reports. Whether those internal pages are written in (X)HTML or XUL. Most of the interacive parts are written in JavaScript. I suppose most of you will by now understand that we are looking for Cross-Site Scripting (XSS) vulnerabilities in the browser interface. What's notable here, is that this bypasses the sandbox.

`about:cache` is actually implemented in C++, but this probably makes its own talk. Ask me later, if you want to know more.

# Act 1, Scene 2 Time travel to 2017
Being equipped with the right kind of knowledge and the crave for a critical Firefox bug under my name, I started using our code search more smartly. Behold:

> Search: `.innerHTML =`
>
> Number of results: 1000 (maximum is 1000)

Hm. Excluding test files.

> Search: `innerHTML =`
>
> Number of results: 414

That's still a lot. And that's not even all kinds of XSS sinks.

> Search (long and hairy regular expression that tries to find more than innerHTML)
>
> Number of results: 997


That's bad. Let's try to be smarter!
Entering the Stage: An security guy with an interest in Static Analysis

# Act 1 Scene 2: An idiot learns Syntax Trees
I've actually dabbled in this space for a long while, even before this episode in 2017. This would be another talk, but a less interesting one. So I'll skip ahead and tell you that I wrote an eslint plugin, that will analyze JavaScript files to look for 

1. Checking the right-hand side in assignments (`+`, `+=`) to `innerHTML`, `outerHTML`.
2. Checking the first argument in calls to `document.write()`, `document.writeln()`, `eval` and `insertAdjacentHTML` (second argument)

For both, we'll check they contain avariable. String literals or empty strings are ignored. The plug-in is available at as [`eslint-plugin-no-unsanitized`](https://github.com/mozilla/eslint-plugin-no-unsanitized) and allows for configuration to detect and ignore built-in escape and sanitize functions. If you're worried about DOM XSS, I recommend you check it out.

# Act 2: The vulnerabilities

Using this nice extension to scan all of Firefox, yields us a handy amount of merely 32 matches. We create a spreadsheet and audit all of them by hand. Lots of dirty work here. Following around long calling chains, with unclear input values and patterns that either escape HTMl close to the final `innerHTML`, upon creation or stuff that's extracted from databses (like the browsing history), which does its escaping upon insertion.

-------
<marquee>Many nights later</marquee>

----

# Act 2, Scene 2: A first bug appears
Heureka! This sounds interesting:
```js
  let html = `
    <div style="flex: 1;
                display: flex;
                padding: ${IMAGE_PADDING}px;
                align-items: center;
                justify-content: center;
                min-height: 1px;">
      <img class="${imageClass}"
           src="${imageUrl}"/>       <----- boing
    </div>`;
  // (...)
  div.innerHTML = html;
```

When hovering over an markup that points to an image in the web developer tools, they will helpfully create a tooltip that preloads and shows the image for the web developer to enjoy. Unfortunately, that URL is not escaped.

# Act 2 Scene 3: Writing the exploit
After spending a few sleepless nights on this, I didn't get anything beyond a XML-conformant proof of concept of  &lt;button>i&lt;/button>. At some point I filed the bug as `sec-moderate`, i.e., this is almost bad, but likely needs another bug to be actually terrible. To summarize, I wrote:

> I poked a bit again and I did not get further than &lt;button>i&lt;/button> for various reasons:

> - the payload is in a URL
> - the injection happens through an innerHTML assignment, so &lt;script>..&lt;/script> won't work
> - reading it from the DOM, JavaScript sees the URL with spaces encoded as %20, which limits the HTML payload significantly
> - finding a way to execute scripts without &ltscript> tags and with all spaces encoded as %20 limits us greatly
> - an obvious avenue for attack would be things like &lt;svg/onload=alert(1)>
> - the current document is a XUL)document, that parses way stricter than normal HTML
> - despite the well-known XML strictness that demands proper quoting and ending tags, it also disallows the trick to replace the space that separates the tag name and the attribute with a forward slash
>
> **In summary: I'd be amazed to see if someone else gets any farther.**

A few nights later, I came up with an exploit that breaks the existing syntax while staying XML conformant.
We visit an evil web page that looks like this:
```html
<img src='data:bb"/><button><img src="x" onerror="alert(Components.stack)" /></button><img src="x'>

```
The image URL that is used in the vulnerable code spans all the way from `data:` the closing single quote at the very end. Our injection alerts `Components.stack`, which indicates that we have left the realms of mortal humans.

This is [Bug 1372112 (CVE-2017-7795)](https://bugzilla.mozilla.org/show_bug.cgi?id=1372112). Further hikes through our spreadsheets of eslint violations lead to [Bug 1371586 (CVE-2017-7798)](https://bugzilla.mozilla.org/show_bug.cgi?id=1371586). Both were fixed in Firefox 56, which was released in the fall of 2017.

We find and fix some minor self-xss bugs (e.g., creating a custom preference in `about:config` with the name of `<button>hi</button>` lead to XUL injections. All of them are fixed and we're fearful that mistakes will be made again.

Critical bugs are a great way to impact coding style discussions and it is decided that the linter might as well be included in all of our linters. `innerHTML` and related badness is forbidden and we rub our hands in glee.
Unfortunately, it turned out that lots of legacy code will not be rewritten and security engineers do not deal with affairs of simple front end engineers (joke's on me in the end though, I promise).
So, we allow some well-audited and finely escaped functions with a granular and exception, that gives us a confident feeling of absolute security (it's a trap!)
```js
// eslint-disable-next-line no-unsanitized/property
```

# Act 3, Scene 1: A Dark Shadow

I feel like I have eradicated the bug class from the entirety of our codebase. We may now look for more complicated bugs and our days get more exciting.

Of course, I wander through the office bragging with my cleverness, warning young folks from the danger of XSS and wear my Security t-shirts super proudly. There's lots of colorful war stories to be told and even more free snacks or fizzy drinks to be consumed.

Meanwhile: My great colleagues that contribute and actually develope shit that's useful. Despite all their good work, some of them even mentor aspiring students and enthusiastic open source fans. Having listened to my stories of secure and well-audited code that should eventually be replaced, they make an effort to get someone remove all of the danger, so we get to live in an exception-less world that truly disallows all without these pesky `eslint-disable-next-line` comments.

Naturally, code is being moved around, refactored and improved by lots of other people in the organization.

So, while I'm sitting there, enjoying my internet fame (just browsing memes, really), people show up at my desk asking me for a quick look at something suspicious:

```js
// eslint-disable-next-line no-unsanitized/property
doc.getElementById("addon-webext-perm-header").innerHTML = strings.header;

// data coming *mostly* from localization-templates
    let strings = {
      header: gNavigatorBundle.getFormattedString("webextPerms.header", [data.name]),
      text: gNavigatorBundle.getFormattedString("lwthemeInstallRequest.message2",
                                                [uri.host]),
// ..
// but of course all goes through _sanitizeTheme(aData, aBaseURI, aLocal)
// (which does not actually sanitize HTML)
```

I feel massively stupid and re-create my spreadsheet. Setting eslint to ignore the `disable-next-line` stuff locally allows me to start all over.
We build an easy exploit that pops calc. How funny! We also notice that a few more bugs like that have crept in, since the "safe" call sites were whitelisted. Yikes.

Having learned about about XML namespaces, a simpler example payload (without the injection trigger) would like look this:

```html
<html:img onerror='Components.utils.import("resource://gre/modules/Subprocess.jsm");Subprocess.call({ command: "/usr/bin/gnome-open" });' src='x'/>,
```

# Act 3, Scene 2: Hope on the horizon

A good patch is made and circulated with a carefully selected group of senior engineers. We have various people working on the code and are concerned about this being noticed by bad actors. With the help of the aforementioned group, we convince engineering leadership that this warrants an unscheduled release of Firefox. We start a simplified briefing for Release Management and QA.

People point out that updates always take a while to apply to all of our release base and shipping a new version with a single commit that replaces `.innerHTML` with `.textContent` seems a bit careless. Any idiot with an less-than sign on their keyboard could write a "1-day exploit" that would affect lots of users.

What can we do? We agree that DOM XSS deserves a heavier hammer and change our implementation for HTML parsing (which is being used in `innerHTML`, `outerHTML`, `insertAdjacentHTML`, etc.). Normally, this function parses the DOM tree and inserts where assigned. But now, for *privileged JavaScript*, we parse the DOM tree and omit all kinds of badness before insertion. Luckily, we have something like that in our source tree. In fact, I have confirmed it's safe and sound in 2013. We also use this to strip HTML email from `<script>` and so on in Thunderbird, so it's even battle-tested.
On top, we do some more due diligence and identify some problems around leaving form elements in, which warrants follow-up patches in the future.

A nice benefit is that a commit which changes how DOM parsing works, doesn't allow reverse engineering our vulnerability from the patch. Neat.

In the next cycles, we've actually been appropriately diligent and removed all sorts badness. This was [Bug 1432966: Sanitize HTML fragments created for chrome-privileged documents (CVE-2018-5124)](https://bugzilla.mozilla.org/show_bug.cgi?id=1432966)

# Closing credits and 
# Acknowledgements
Exploitation and Remediation were achieved with the support of various people. Thanks to, security folks, Firefox engineers, release engineers, QA testers. Especially to  Johnathan Kingston (co-maintainer of the eslint plugin), Johann Hofman, who found the bad 0day in 2018 and helped testing, shaping of and arguing for an unscheduled release version of Firefox.

No real geckos were harmed in the making of this play.

# Closing Scene / Easter Egg
Primates acidentally discovering fire – then, wondering about `location.href =`, `location =`, `setTimeout()`, `setInterval()` and so on.

