Title: A CDN that can not XSS you: Using Subresource Integrity
Date: 2015-07-19
Slug: using-subresource-integrity
Author: Frederik

*This blog post is the text-version of my presentation from OWASP AppSec EU 2015. You can [download the slides](https://people.mozilla.org/~fbraun/files/sri-appseceu2015.pdf) or [watch the video on YouTube](https://www.youtube.com/watch?v=JOcpIF047xs)*

## Introduction

In this blog post, I explain [Subresource Integrity (SRI)](https://w3c.github.io/webappsec/specs/subresourceintegrity/), of which I am one of the co-editors. SRI is an upcoming W3C standard that allows securing third-party loads of JavaScript and CSS. This is achieved by comparing the content with a cryptograhic digest that is contained within the surrounding HTML tag.

### Motivation

Many websites use Content Delivery Networks (CDNs) to improve website performance and save on bandwidth. Loading a popular libraries in a common version from a CDN has a high likelihood of being already in your visitor's cache. A lot of CDNs also provide metrics. 

The problem I see with CDNs is that you are increasing the risk surface of your web application: If your own setup is relatively secure, the attacker may just go ahead and attack the CDN instead.

This is because JavaScript files included on your HTML execute within the scope of your application: This spans everything that is on the same scheme (HTTP or HTTPS), domain name and port (i.e., on the [*same origin*](https://en.wikipedia.org/wiki/Same-origin_policy#Origin_determination_rules). [See here for more](https://annevankesteren.nl/2015/02/same-origin-policy)). This implies not only access to all web content, which may be sensitive information like user names, passwords and email address. The script is also allowed to fully interact with the DOM, the cookies and all permissions given to the current website (e.g., Geolocation, Notifications, etc.).

 
Furthermore, attackers that are interested in targeting a lot of users (and not just *your* web application) will go for popular CDNs to gain a very high impact - [as we have seen with DDoS attacks against GitHub](https://blog.cloudflare.com/an-introduction-to-javascript-based-ddos/).

But reducing this attack surface is not that complicated In fact, we already know exactly what file we want to include. There is no need to allow arbitrary scripts from a third-party to go wild within your web page. If only we could check the file before executing it.

### Subresource Integrity to the Rescue

You *can* now check that the scripts matches exactly what you wanted to include, when you originally wrote your web page!

Subresource Integrity (SRI) allows specifying the *digest* of the file that you want to include. The digest is the output of a cryptographic hash function, which helps us achieve integrity.

The idea is that you provide a short `integrity` attribute, which will help the browser decide if the file has been modified. This works because a hash function gives a completely different output every time someone modifies the file.


## Using Subresource Integrity

**Subresource Integrity is an upcoming W3C standard to secure script and style loads from other domains**.

Just add an `integrity` attribute to your script tag.

##### Scripts

```html
<script src="https://code.jquery.com/jquery-1.10.2.min.js"
        integrity="sha256-C6CB9UYIS9UJeqinPHWTHVqh/E1uhG5Twh+Y5qFQmYg="
        crossorigin="anonymous"></script>
```

##### Styles

```html
<link rel="stylesheet" href="https://site53.example.net/style.css"
      integrity="sha256-vjnUh7+rXHH2lg/5vDY8032ftNVCIEC21vL6szrVw9M="
      crossorigin="anonymous">
```

### Computing the `integrity` value
The value of the `integrity` attribute forms a tiny micro-syntax, that is the name of the cryptographic hash function (e.g. sha256) and the output that it has given us.

An example is given in the [SRI specification](https://w3c.github.io/webappsec/specs/subresourceintegrity/#integrity-metadata):
```
$ echo -n "alert('Hello, world.');" | openssl dgst -sha256 -binary | openssl enc -base64 -A
qznLcsROx4GACP2dm0UCKCzCG+HiZ1guq6ZZDob/Tng=
```

Just prefix this with `sha256-` and you're done.


### What is this `crossorigin` attribute?
It is usually not allowed to read the content of files on other domains (rather: origins). It only works if the domain explicitly allows this. In short, SRI requires [CORS](https://annevankesteren.nl/2012/12/cors-101) to work. The `crossorigin` attribute tells the browser to fetch the file in a way that allows reading it afterwards or fail if CORS is not supported. Fortunately, a lot of CDNs already [enable cors](http://enable-cors.org/).

### Multiple hashes

You can provide multiple tokens of integrity metadata (i.e., hashname, dash and value) in one `integrity` attribute. If they contain different hash functions, the browser will pick and prioritize the strongest.

You can also specify multiple values with the same hash function. This is useful when you expect one of many possible resources behind a URL. This can happen because of browser sniffing, or when you expect an update to a file that should not break the page.

### Error Recovery & Reporting

Despite earlier attempts, there is no error recovery or error reporting functionality in Subresource Integrity for now.

You need to recover from failed script loads, otherwise your website may break. A typical attempt would be to load the desired third-party library from an (un-cached) copy on your own origin:

```html
<script src="https://code.jquery.com/jquery.min.js"
        integrity="sha256-C6CB9UYIS9UJeqinPHWTHVq…"
        crossorigin="anonymous"></script>
<script>window.jQuery || document.write('<script src="/jquery-.min.js"><\/script>')</script>
```

You could also use [`navigator.sendBeacon`](http://www.w3.org/TR/beacon/) to log this, if you have an infrastructure for error reporting.

### Tooling

There are already some tools that help using Subresource Integrity.

* [sri-toolbox](https://github.com/neftaly/npm-sri-toolbox) generates valid integrity metadata (hash name, dash, digest)
* [Ember.js plugin](https://github.com/jonathanKingston/ember-cli-sri)
* [broccoli plugin](https://github.com/jonathanKingston/broccoli-sri-hash)

### Implementation Status

Subresource Integrity is coming to mainline browsers soon ([Firefox](https://bugzilla.mozilla.org/show_bug.cgi?id=992096), [Chrome](https://codereview.chromium.org/566083003/) or use a [Polyfill](https://github.com/w3c/webappsec/tree/master/polyfills/subresourceintegrity)). You can [test SRI support on srihash.org](https://srihash.org/).
 
## Conclusion

Loading your scripts and styles from a Content Delivery Network (CDN) can harm your website, if the CDN gets compromised or becomes malicious. 
You can add `integrity` attributes to secure your third-party scripts & styles. This greatly diminishes security risks, as any change to those files will be detected and prevented by the browser.
