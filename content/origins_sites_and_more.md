title: Origins, Sites and other Terminologies
Author: Frederik Braun
Date: 2023-01-14
tags: websecguide

In order to fully discuss security issues, their common root causes and useful prevention or mitigation techniques, you will need some common ground on the security model of the web. This, in turn, relies on various terms and techniques that will be presented in the next sections.

Feel free to skip ahead, if you are familiar with some of the following concepts.

## The Same-Origin Policy

The most important notion of scope on the web is an *Origin*.
An origin is usually a tuple of a scheme, a host and a port of a URL.
Generally, documents can only interact with each other when hosted
on the same origin. In essence, this means that two communicating
documents' URLs should have the same scheme, host and port.

However, an origin can also be a so-called an *opaque origin*, which is considered a restricted context that is always *cross-origin* to everything else. This is used in e.g., `<iframe>` elements with the `sandbox` attribute.

Cross-origin resources that are loaded into the current document (e.g., scripts, images) can be *used* (e.g., executed or displayed) but not properly read: A cross-origin image can be drawn onto a `<canvas>`, but its pixels can not be read. A cross-origin's script can be executed but the actual source text is unreadable. However, the script's side effects are observable when modifying the global scope (e.g., defining a new global variable). This can lead to unintended leaks, called Cross-Site Script Inclusions. <!-- TODO: task: add ref -->

The Same-Origin Policy can not always apply purely based on comparing the origins of two URLs, as we will likely see in another post. For now, a quick link to my 2012 diploma thesis *["Origin Policy Enforcement in Modern Browsers"](https://frederik-braun.com/publications/thesis/Thesis-Origin_Policy_Enforcement_in_Modern_Browsers.pdf)* will have to suffice.

Interactions that are subject to the Same-Origin Policy can be roughly grouped in two scenarios:

### 1) DOM Access

Synchronous access in JavaScript across origin boundaries can happen through a `window` or `document` object. These are typically obtained through an `<iframe>` or a popup created with `window.open()` and are always gated by the Same-Origin Policy - except for some interesting corner cases:

1. Reading the `window.length` property, which reveals the number of frames.
2. Reading `closed` attribute (used for popups) and calling `close()`.
3. Invoking `focus()` and `blur()`.
4. Calling `postMessage` allows sending data, which triggers a `MessageEvent` on the receiving window asynchronously.
5. A cross-origin window *can* be navigated away by assigning to `window.location` or invoking `location.replace()`.

Interestingly, this already allows for some tricks and attacks where a cross-origin window is suddenly replaced with a similar-looking spoof.

### 2) HTTP Requests

Websites can perform HTTP requests, but will *not* be able to read the responses, unless the request's URL is same-origin. Requests are typically issued with APIs like `XMLHttpRequest` and `fetch()`.

However, there are some exceptions and techniques towards relaxing same-origin checks, like *Cross Origin Resource Sharing* (CORS). Many of these exceptions grew organically based on some specific need. We will go through them in a later post.
<!-- TODO: task: add ref-->

## Site, Registerable Domain and Public Suffix

Some APIs are governed by the notion of a *Site*, instead of an *Origin*. A *Site* is a combination of a scheme and a host's *registerable domain*.

Looking up the *registerable domain* of a hostname, is a quite literally a check which domain had to be registered (e.g., `example.co.uk` or is the registerable domain for `www.example.co.uk` as well as for `mail.example.co.uk`). This lookup is useful to include an entity and all of its subdomains, but nothing above.

The idea of a *Site* is used in a variety of specs that want to allow related web pages to collaborate for convenience or legacy support reasons. Among them are Storage Access API (3rd Party Cookie Access), WebAuthn and Federated Credential Management.

<blockquote>
<b>Historical context</b>:

Previously, people used the terminology of a <em>top-level domain</em>, where the <em>top</em> was presumed to be exactly one level of nesting and not more. This has been long-since incorrect and impractical - given the existence of "top" levels with additional nesting like <code>co.uk</code>. Therefore, a variety of other terms have emerged, like <em>eTLD+1</em> (the effective top-level domain, plus another level of nesting). Web standards have converged on <em>registerable domain</em>.<br>
What this means is that the boundary where a "top" level begins has to be defined otherwise: In practice, this happens in a manually maintained text file otherwise known as the <em><a href="https://publicsuffix.org/">Public Suffix List</a></em>.
<br><br>
Aside: Even before that, people used to refer to same-site by just comparing two <em>registerable domains</em>, without the scheme. This has been renamed to <em>schemelessly same-site</em>. Let's pretend that never happened in the first place.
</blockquote>

Getting a domain of yours added to the aforementioned Public Suffix List, allows to enforce privilege separation along the lines of the Same-Origin Policy: If your domain is considered a public suffix, then every name below that becomes its own origin. It is generally recommended to do that in order to assign user-generated content into separated namespaces. A great example is `github.io`, where each user is getting a namespace underneath the public suffix and can therefore not affect cookies or site-specific settings with other users.

## Secure Contexts

*Secure Context* is a generalized notion of whether a website was served over HTTPS. A simple look at the protocol scheme does not fully work and the generalization is necessary to allow for situations where a document does not have a HTTP(S) URL but is inheriting its context (e.g., `<iframe srcdoc>`, `about:blank` documents). Additionally, pages hosted on `*.localhost` or via the local filesystem (`file://`) are also considered secure. Whether the current page was delivered securely is exposed in JavaScript via the `window.isSecureContext` property.

Being in a Secure Context is often times required for newer, powerful APIs which want some level of assurance that a web page has not been intercepted or modified by a network attacker. A typical API that requires it is ServiceWorkers, because persistently installed background code should not be perpetuated into future sessions when coming from an insecure connection.

**Note:** A document delivered over HTTPS is **not** a secure context, if it has been embedded from an insecure context (e.g. HTTP site contains `<iframe>` of HTTPS site).

## Cross-Origin Isolation

Cross-Origin Isolation is a newer security boundary, that was created as a reaction to two noteworthy attack groups. The first attack group being so-called cross-site leaks (henceforth called *xsleaks*) and microarchitectural side-channel attacks against modern CPUs (Spectre, Meltdown, and its various successors).

*Xsleaks* attacks rely on abusing some pre-existing global state (e.g. browser cache, a resource limit for maximum allowed opened socket) to infer or leaking cross-site application state. This is a generalization upon previously known methods for e.g., redirection-detections to identify whether a user is logged in with a third-party site, but also history stealing attacks<!-- this could need way more details. -->. The [xsleaks wiki](https://xsleaks.dev/) has many examples and suggested countermeasures.

Microarchitectural attacks (like Spectre and Meltdown) rely on specific CPU behavior in order to infer or leak information from the processor itself. Roughly speaking, exploitation allows to read arbitrary memory within the same operating system (OS) process. Carrying out a Spectre attack, for example, is believed to be possible using shared memory access and high-precision timers. Both exist as APIs provided by the web platform with `SharedArrayBuffer` and the Performance API.

As a result, an attacker would have been able to violate the Same-Origin Policy by embedding a cross-origin resource (using e.g., an `<img>` element) and reading process memory. As a reaction, browser engines have originally disabled access to those APIs or reduced timing granularity.

Despite blocking Web APIs, major browsers like Chrome and Firefox have also gone through significant re-architecturing efforts to create and assign separate OS-processes to websites of different *Sites*. These long-term engineering projects (called *Site-Isolation*) were mostly without side effects for web developers. However, this is not enough, given the embedding attack example above.

In order to reenable access to these coveted APIs, a website now has to ensure that is not including any cross-origin content (using `Cross-Origin-Embedder-Policy` or *COEP*) or only content that has been explicitly listed as public across process boundaries by its author (using `Cross-Origin-Resource-Policy`). Furthermore, the web page needs to disallow synchronous window handle access using the `Cross-Origin-Opener-Policy` (also known as *COOP*).

When used in combination, COEP and COOP lead to the `window.crossOriginIsolated` property becoming `true`. This give access to the `SharedArrayBuffer` constructor and high-precision timing in the Performance API.

To summarize, *Cross-Origin Isolation* and is a mechanism to retrofit the web  security model in light of new attacks: A website can only get access by being assigned its very own, unique browser process that is also free of potentially sensitive cross-origin content.

## What else?
Do you feel like something is unclear or missing?
