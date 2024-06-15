Title: What is mixed content?
Date: 2024-06-15
Author: Frederik
Slug: mixed-content
tags: websecguide

In web security, you may have heard of "mixed content". This blog post
is going to explain what it means, its implications for your website and
how to handle mixed content.

# Mixed Content: active or passive?

When hosting a web page on secure HTTPS, as it should be the default nowadays,
the term "mixed content" refers to content on your web page that is *not* using
HTTPS. Typical examples are images in `<img>` tags, stylesheets or scripts.
Ideally, a website that supports HTTPS should ensure that all its content is
also secured with HTTPS. Otherwise, the protection against network attackers
that is gained with HTTPS could be compromised: When the browser visits a web
page that uses mixed content, a passive network attacker can gain information
about the user's browsing behavior because of those unprotected mixed content
URLs in the web page. Furthermore, an active network attacker could replace or
modify the mixed content and therefore attack the whole home page.

Browsers have long since included protection against the harms of mixed
content. Already in [July 2014, a first working draft came out in the W3C
web application security working
group](https://www.w3.org/TR/2014/WD-mixed-content-20140722/),
that suggested browsers should block so-called *active* mixed content.
Originally, this referred to `<script>` and `<iframe>` elements, ensuring
that a network attacker can not modify or inject scripts into a victim page.
Other, so-called "passive" content, like images were still allowed. Back then,
this move had the goal of
[supporting existing content](https://www.w3.org/TR/html-design-principles/#support-existing-content)
which still used a *lot* of HTTP. The active attacks where thwarted, but
passive attackers would still be able to infer browsing behavior through
network sniffing.

From then on, future HTML elements and features, like responsive images in
`<picture>` elements were all considered "active" elements and supposed
to be blocked.

# Upgrade Insecure Requests

Right after that, the webappsec working group developed a new directive for
Content-Security-Policy (CSP) headers. Web pages that want their mixed
content to be secure can supply a response header of
`Content-Security-Policy: 'upgrade-insecure-requests'` and the browser will
implicitly rewrite *all* HTTP URLs into HTTPS. This includes passive and
mixed content. Hyperlinks with an `<a>` however, are only rewritten when they
refer to the
[same-origin](https://frederikbraun.de/origins-sites-and-other-terminologies.html).
But again, this upgrading is all opt-in.

# Mixed Content: upgradable and blockable.

Then, in year 2020, the engineers in the Chrome browser's network security
group did a  thorough study to learn more about mixed content that is
still loading on web pages.

The outcome was an even newer, improved [Mixed
Content](https://www.w3.org/TR/mixed-content/) standard. As of 2024,
browsers no longer distinguish between "active" and "passive" mixed content.

At this point, all browsers will instead distinguish between *blockable* and
*upgradable* mixed content. Where the former is stuff that has already been
blocked, like `<script>`, `<iframe>`, and we assume we can't start loading
lest sites break again. The latter is the passive content that we have
previously loaded insecurely.

In essence, web pages that are hosted on HTTPS and contain image, audio or
video elements pointing to HTTP will receive an automatic, implicit upgrade.
Browsers will still not upgrade `<a>` elements that point to same- or cross-
origin URLs.

Now, if you want your same-origin URLs to be redirected, you can use
an [HTTPS `Strict_Transport-Security`
header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)
or set a `Content-Security-Policy` with `'upgrade-insecure-requests'` to
upgrade all, the *blockable*, the *upgradable* content and the `<a>` elements.