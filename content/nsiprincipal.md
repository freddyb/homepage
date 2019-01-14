Title: What's in a Principal
Date: 2019-12-12
Author: Frederik


# What's a Principal
Hackers interested in browser security and developers of Gecko alike will you will sooner or later hear about the *Principal*, a concept that is somewhat unique to the Mozilla source code.
This blog posts covers the most important information about principals, how Gecko does security decisions while loading resources and the [nsIPrincipal](https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Reference/Interface/nsIPrincipal) interface in particular.

## A Principal is an Origin - and more
For most typical web loads, the Principal is merely an implementation of an Origin. As a reminder, an origin is the triple {scheme, host, port} of a URL. So, the implementation of the [Same-Origin Policy](https://en.wikipedia.org/wiki/Same-origin_policy) is a comparison of two principals.
Most importantly, we never use the URL directly. We always use the principal. A principal object is often times accessible as a member of the relevant class (e.g., the Document) or easily available through `NodePrincipal()`.
However, there are four *kinds of principals* that are worth looking at more closely.

### ContentPrincipal (aka Codebase Principal)
For web resources, the principal is easily inferred from the URL. In Gecko, we call web-hosted resources *content*, hence ContentPrincipal.
The most used type of principal is the web-like principal for web resources. In Gecko, these are called content principals or codebase principals.

### SystemPrincipal
The SystemPrincipal is used for privileged code that implements the frontend of Firefox. The SystemPrincipal passes all security checks.

### NullPrincipal
A NullPrincipal is used for minimally privileged security contexts, for example in `<iframe sandbox>` and documents loaded from `data:` URLs.
This means that the Nullprincipal is not equal to any other principal (including other null principals).

### ExpandedPrincipal
ExpandedPrincipals are used within extensions.[Content Scripts](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Anatomy_of_a_WebExtension#Content_scripts) are more privileged than normal web pages, but also able to assume the security context of a website. ExpandedPrincipals are best understood as a list of other principals. Security checks on ExpandedPrincipals are implemented as a loop through an internal allow list and requires at least one of the entries to pass.

## Origin Attributes
- FIXME: link to the nice paper
- FIXME maybe skip and add to a later blog post

## What to consider when you do a load (LoadInfo)


### Further reading
* [nsIPrincipal on MDN](https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Reference/Interface/nsIPrincipal)
* [Principal (computer security) on Wikipedia](https://en.wikipedia.org/wiki/Principal_(computer_security))
* [Script security on MDN](https://developer.mozilla.org/en-US/docs/Mozilla/Gecko/Script_security)



