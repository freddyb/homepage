# Chrome switching the XSSAuditor to filter mode re-enables old attacks

Recently, Google Chrome changed the default mode for their Cross-Site Scripting
filter *XSSAuditor* form `block` to `filter`. This means that instead of
blocking the page load completely, XSSAuditor will now continue rendering the
page but modify the bits that have been detected as an XSS issue.

In this blog post, I will argue that the filter mode is a dangerous approach
by re-stating the arguments from the whitepaper titled
[X-Frame-Options: All about
Clickjacking?](https://frederik-braun.com/xfo-clickjacking.pdf)
that I co-authored with [Mario Heiderich](https://heideri.ch/) in
2013.

After that, I will elaborate XSSAuditor's other shortocmings and revisit
the history of back-and-forth in its default settings.
In the end, I hope to convince you that XSSAuditor's contribution is
not just neglegible  but really negativ and should therefore be removed
completely.

<hr>

## JavaScript à la Carte
When you allow websites to frame you, you basically give them full permission to
decide, what part of JavaScript of your very own script can be executed and what
cannot. That sounds crazy right? So, let’s say you have three script blocks on
your website. The website that frames you doesn’t mind two of them - but really
hates the third one. maybe a framebuster, maybe some other script relevant for
security purposes. So the website that frames you just turns that one script
block off - and leave the other two intact. Now how does that work?

Well, it’s easy. All the framing website is doing, is using the browser’s XSS
filter to selectively kill JavaScript on your page. This has been working in IE
some years ago but doesn’t anymore - but it still works perfectly fine in
Chrome. Let’s have a look at an annotated code example.

Here is the evil website, framing your website on example.com and sending
something that looks like an attempt to XSS you! Only that you don’t have any
XSS bugs. The injection is fake - and resembles a part of the JavaScript that
you actually use on your site:

```html
<iframe src="//example.com/index.php?code=<script src="/js/security-libraries.js"></script>"></iframe>

```

Now we have your website. The content of the code parameter above is part of
your website anyway - no injection here, just a match between URL and site
content:

```html
<!doctype html>
<h1>HELLO</h1>
<script src="/js/security-libraries.js"></script>
<script>
// assumes that the libraries are included
</script>
```

The effect is compelling. The load of the security libraries will be blocked by
Chrome’s XSS Auditor, violating the assumption in the following script block,
which will run as usual.

## Existing and Future Countermeasures
So, as we see defaulting to `filter` was a bad decision and it can be overriden
with the `X-XSS-Protection: 1; mode=block` header. You could also disallow
websites from putting you in an iframe with `X-Frame-Options: DENY`, but it
still leaves an attack vector as your websites could be opened as a top-level
window. (The `Cross-Origin-Opener-Policy` will help, but does not yet
ship in any major browser). Surely, Chrome might fix that one bug and stop
[exposing `onerror` from internal error pages
](https://portswigger.net/blog/exposing-intranets-with-reliable-browser-based-port-scanning).
But that's not enough.

## Other shortcomings of the XSSAuditor
XSSAuditor has numerous problems in detecting XSS. In fact, there are so many
that the [Chrome Security Team does not treat bypasses as security bugs in
Chromium](
https://chromium.googlesource.com/chromium/src/+/master/docs/security/faq.md#are-xss-filter-bypasses-considered-security-bugs).
For example, the XSSAuditor scans parameters individually and thus allows for
easy bypasses on pages that have multiple injections points, as an attacker can
just split their payload in half.
Furthermore, XSSAuditor is only relevant for reflected XSS vulnerabilities. It
is completely useless for other XSS vulnerabilities like persistent XSS,
Mutation XSS (mXSS) or DOM XSS. DOM XSS has become more prevalent with the
rise of JavaScript libraries and frameworks such as jQuery or AngularJS.
In fact, a 2017 research paper about exploiting DOM XSS through so-called
*script gadgets* discovered that [XSSAuditor is easily bypassed in 13 out of 16
tested JS frameworks
](https://github.com/google/security-research-pocs/blob/master/script-gadgets/ccs_gadgets.pdf)


## History of XSSAuditor defaults
Here's a rough timeline

- *2010* - Paper "Regular expressions considered harmful in client-side XSS
filters" published. Outlining design of the XSSAuditor, Chrome ships it
with default to `filter`
- *2016* - [Chrome switching to `block` due to the attacks with non-existing
injections](https://groups.google.com/a/chromium.org/forum/#!msg/blink-dev/aZsNygF84JM/86EbD_q0CAAJ)
- *November 2018* - [Chrome error pages can be observed in an iframe, due to
the `onerror` event being triggered
twice](https://portswigger.net/blog/exposing-intranets-with-reliable-browser-based-port-scanning),
which allows for cross-site leak attacks
](https://github.com/xsleaks/xsleaks/wiki/Browser-Side-Channels#xss-filters).
* *January 2019* (hitting Chrome stable in April 2019) - [XSSAuditor switching
back to
`filter`](https://chromium-review.googlesource.com/c/chromium/src/+/1417872)

## Conclusion
Taking all things into considerations, I'd highly suggest removing the
XSSAuditor from Chrome completely. In fact, [Microsoft has announced they'd
remove the XSS filter from Edge](
https://blogs.windows.com/windowsexperience/2018/07/25/announcing-windows-10-insider-preview-build-17723-and-build-18204/)
last year. Unfortunately, a [suggestion to retire XSSAuditor initiated by the
Google Security Team](
https://bugs.chromium.org/p/chromium/issues/detail?id=898081&desc=2) was
eventually dismissed by the Chrome Security Team.

<footnote><small>
This blog post does not represent the position of my employer.<br>
Thanks to Mario Heiderich for providing valuable feedback:
Supporting arguments and useful links are his. Mistakes are all mine.
</small></footnote>