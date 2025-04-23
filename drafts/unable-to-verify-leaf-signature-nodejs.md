Title: Fixing UNABLE_TO_VERIFY_LEAF_SIGNATURE...
Date: 2024-12-01
Author: Frederik
slug: unable-to-verify-leaf-signature-nodejs
tags: websecguide

## ...and what are intermediate certificates anyway?
Just last week my colleague Andi from [MDN Web Docs (one of the best websites ever)](https://developer.mozilla.org/), asked me about a issue he had encountered in the [MDN Observatory](https://developer.mozilla.org/en-US/observatory) backend.
For those who don't know the [Observatory](https://developer.mozilla.org/en-US/observatory) yet, it's a web page that allows you to get a quick web security check for your web page. (My web page gets an A+. This is no  coincidence. And yours?)
The issue occured when checking a third-party site and the error message was **`UNABLE_TO_VERIFY_LEAF_SIGNATURE`**. Clearly, this is is something about HTTPS / TLS. But the odd thing is that the web pag worked *just fine* in Firefox. Why?

### Intermediate Certificates

The core issue is easier explained when looking at how certificates are typically created (and valideted). To get a trusted certificate for your website, you need to work with a Certificate Authority (CA). This is to ensure that the domain in the certificate is only usable by the owner of the domain.
Most of this is easily automated thanks to Let's Encrypt and the ACME protol (not in scope for this blog post :-)). In essence, you can easily create a certificate for your domain, prove that it is actually yours and have it signed such that every browser can verify your certificate as trustworthy.
This works because your browser (or really any TLS/HTTPS  client) has a list of CAs (like Let's Encrypt) pre-insalled and can therefore validate a certificate by verifying a cryptographic signature.
What's mostly hidden from the end user is that CAs need to keep their cryptographiy key material super secure to ensure it is not exposed to the internet. So, how do they sign a load of certificates while keeping their keys secured? The solution are so-called Intermediate certificates (or Intermediates). A CA typically creates a set of certificates which are also marked as CA ceriticates that then do the actual signing of certificates for the web. In case of Let's Encrypt, there are currently [two Intermediates that are signed by two roots](https://letsencrypt.org/certificates/) (both are signing both). This essentially means that the steps to validate a certificate is now a bit longer. In terms of tree metaphors, the path goes from the root CA to the Intermediate to the so-called leaf certificate (which is for your domain).
For your client, that means it needs to know of the intermediate as a trusted entity signed by the root to verify that a web site's certificate is valid.
The usual way to solve it is that a web server should not present its own certificate but a full chain that goes up to a trusted root. Tools like `cerbot` for Let's Encrypt usually do that [by default](https://eff-certbot.readthedocs.io/en/stable/using.html#certbot-command-line-options).
But what if it doesn't?

### Intermediate Preloading

While it was long believed as a misconfiguration when a web site can not show a full proof of validity, browsers have stepped in to fix this. Even though Intermediates can change more often than Root CAs, they can still be loaded into the browser.
A typical fix is to load them dynamically as part of browser settings rather than making them part of the browser release. Firefox calls this [Intermediate Preloading](https://blog.mozilla.org/security/2020/11/13/preloading-intermediate-ca-certificates-into-firefox/).
While preloading fixes this for browsers and their end users, the missing intermediate is still an issue for other clients out there.
And that is why `node` is sometimes reporting an error to verify a leaf signature.

### Fixing this in nodejs

There are various posts on the internet on how to fix this, some suggest to just not validate certificates at all. (This is where you realize that the motivation for this very blog post may have been ["Someone is wrong on the internet"](https://xkcd.com/386/). But it's also because I replied to Andi's question with a very long monologue that I found worth capturing here).

**The best fix is to supply node with the extra intermediates.** As mentioned above, Intermediates can change more often than roots, so they should be maintained independently and more often. The good thing is that all Certificate Authorities need to disclose their Intermediates and the great [Common CA Database (CCADB) project](https://www.ccadb.org/resources) has a list.

In nodejs, you can set the environment variable `NODE_EXTRA_CA_CERTS` to a file path that has an additional certificate bundle.
