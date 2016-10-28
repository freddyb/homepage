Title: Subresource Integrity
Date: 2014-10-05
Slug: subresource-integrity
Author: Frederik

**This article has been superseded by a [more-recent write-up](https://frederik-braun.com/using-subresource-integrity.html) of my presentation from OWASP AppSec EU 2015. Alternatively, you can [download the slides](https://people.mozilla.org/~fbraun/files/sri-appseceu2015.pdf) or [watch the video on YouTube](https://www.youtube.com/watch?v=JOcpIF047xs)**

Some time ago, I complained about the prevalence of CDNs for JavaScript
hosting and the trust model that comes with including JS files
into your web page: Every script may read and request towards *everything*
that is on your this website and all your other websites. This is because of the
[Same-Origin Policy](https://en.wikipedia.org/wiki/Same-origin_policy).

After that, Brad Hill (co-chair of the
[W3C Web Application Security Working Group](http://www.w3.org/2011/webappsec/))
asked me to help co-edit[^1] one of the deliverables for the working group:
A possible feature for the web platform to ensure that resources embedded
or included in a document (e.g. script files from other origins) have not
been tampered with and are indeed the ones the content author intended
to use. This upcoming specification is called
[Subresource Integrity](http://www.w3.org/TR/SRI/) (SRI)[^2] .


The idea is that we include a third party script along side a
cryptographic hash of its content. The web browser may then compute the
hash on retrieving the file and compare if it's the one it expected to
receive. This is how this would look in mark-up:

```html
<script src="https://analytics-r-us.com/track.js"
        integrity="ni:///sha-256;SDfwewFAE...wefjijfE?ct=application/javascript"></script>
```

While certainly not aesthetically appealing, we are using this `ni://`
notation because it is already defined in
<a href="https://www.rfc-editor.org/rfc/rfc6920.txt" title="RFC 6920: Naming Things with Hashes">RFC 6920</a>.
This mostly saves us time explaining things in the spec and might allow
implementations to re-use existing code. The first half of the `ni://`
URL explains which hashing function to use (i.e., SHA-256) while the
second part contains the base64url encoded[^b] digest that SHA-256
produces on the content of the script. The `ct` bit says explicitly what
kind of content we should expect. This defends against content type
spoofing attacks.

#### Does this mean a script update breaks my web page?

Your website does not *have to* break when the script file changes.
The previous example given does indeed block a script once the file
changes. And this *may* make your website unusable. But you can also
provide a fallback mechanism:
you simply say that the script should be loaded from a CDN that is fast
and likely cached within the browser. But it *must* match the hash.
If this is *non canonical* location does not work, the browser can still
load the file from your own domain - albeit a little slower:

```html
<script src="http://example.com/script.js"
        noncanonical-src="http://cdn.example.com/script.js"
        integrity="ni:///sha-256;jsdfhiuwergn...vaaetgoifq?ct=application/javascript"></script>
``` 

See how we changed the attributes? Now `src` points to the file that you
host yourself. And the CDN is mentioned as a *non canonical* source.
This will make the website work for every case. But you still get the
speed bonus from the CDN.

#### Content addressable storage: More than a CSP Bypass?

A useful feature that piggy-backs on SRI might be content-addressable
storage: The idea is, once you can identify a resource by its hash, you
could save yourself the trouble and asking the server for it, if it's
already cached from some other domain.

The problem that comes with this idea is cache poisoning: The client
still has to find out if the server really hosts this file. Otherwise
an attacker could trick your browser into believing that you host files
which you don't. Content injection (XSS) may then use a previously
stored hash so that it looks like you are hosting the evil JavaScript
payload that the browser has previously seen on evil.com. This nifty
attack was raised by [Michal Zalewski](http://lcamtuf.coredump.cx/) on
the webappsec w3c mailing list.
My co-worker [Mark Goodwin](https://computerist.org/) suggests that we
may allow this for hashed files that are already allowed through hashes
in [CSP 2 script-src hashes](http://www.w3.org/TR/CSP2/#script-src-hash-usage).


#### The foul fruit called integrity-checked active mixed content

Another idea that has been raised on the mailing list was
[mixed content](https://developer.mozilla.org/en-US/docs/Security/MixedContent):
Modern browsers currently block active mixed content, i.e., plain-HTTP
scripts on HTTPS websites. Somebody suggested we might disable this
blocking if SRI is used to make sure that the resource has not been
tampered with. While this is a reasonable argument for the functionality
of the script, it leaves out the confidentiality aspects: HTTPS is also
about confidentiality, and I contend we should continue blocking active
mixed content, even if it contains an SRI `integrity` attribute.

What I *do* like is that this suggestion looks at JavaScript as a means to
deliver software. And I hope that SRI can play a part in the story of
making software (i.e., script) delivery on the web a bit more secure.

#### SRI helps WebCrypto

The story with WebCrypto could really improve through SRI: Although
WebCrypto is
[considered harmful by Matasano Security](http://matasano.com/articles/javascript-cryptography/),
I think SRI could fix some of the [things that are wrong with webcrypto](http://tonyarcieri.com/whats-wrong-with-webcrypto):
The reality is, more and more applications are implemented as web applications.
Firefox OS has taught me that backend-less, JavaScript-only
applications can power a full phone operating system. And these systems
really *need* crypto. The question is just how we do it: It is much
safer to use something provided by the platform than using pure JavaScript
Cryptography[^3]. I also think that a tiny web page may bootstrap an
application and verify that trusted code has indeed not been tampered
with, by including all subresources with `integrity` attributes.
This tiny web page may even be stored locally as a safe entry point into
websites that use WebCrypto.

#### Site-wide Subresource Integrity with CSP

Subresource Integrity plans to extend CSP to include an
[integrity-policy directive](http://www.w3.org/TR/SRI/#handling-integrity-violations-1).
This would allow you to apply integrity checks for all resources on
your site. And this also means that a failed integrity check
will be reported just like CSP violations. You will then be able to
enforce and verify integrity for your whole web page.


#### Implementation Status

Subresource Integrity is not in your browser. Google Chrome has an
[implementation](https://codereview.chromium.org/566083003/) that works only for scripts and only on secure origins
(e.g. HTTPS websites). A similarly reduced
[implementation for Firefox](https://bugzilla.mozilla.org/show_bug.cgi?id=992096)
is currently planned.
Those attempts also exclude `integrity-policy` in CSP and violation
reports. In the long run we still want integrity checks for all
kinds of subresources (e.g., images, styles, iframes).


[^1]: The spec is joint work with some brilliant people: Devdatta Akhawe from UC Berkeley and Joel Weinberger and Mike West from Google.
[^2]: It is currently in an early state, that is called "First Public
Working Draft. And by the way: The worst thing you can do to your inbox
is have your email address published on a W3C website.
[^3]: Thinking about timing attacks, for example.
[^b]: The url-safe Base64 encoding is explained in [RFC4648: The Base16, Base32, and Base64 Data Encodings](http://tools.ietf.org/html/rfc4648).
