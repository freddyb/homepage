Title: What's in a Principal
Date: 2019-12-12
Author: Frederik


# What's in a Principal
Those working on Gecko, the rendering engine of Firefox, will sooner or later hear about the *Principal*. This blog posts covers the most important information about principals, how Gecko does security decisions while loading resources and the [nsIPrincipal](https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Reference/Interface/nsIPrincipal) interface in particular.

## Four Kinds of Principals
For most typical web loads, the Principal is merely an implementation of an Origin. As a reminder, an origin is the scheme, host and port of a URL. So, the [The Same-Origin Policy](https://en.wikipedia.org/wiki/Same-origin_policy) is comparison of two principals.


> *"The principal is merely the implementation of an Origin"*



### ContentPrincipal (aka Codebase Principal)
In Gecko, we call web-hosted resources *content*. This follows from the fact that both websites and the user interface (the browser chrome, or just *chrom** for short) are implemented with web technologies like HTML, CSS and JavaScript.
The most used type of principal is the web-like principal for web resources. In Gecko, these are called content principals or codebase principals.

### SystemPrincipal
The system principal is
 subsumes itself and all other principals.

### NullPrincipal
A null principal (corresponding to an unknown, hence assumed minimally privileged, security context) is not equal to any other principal (including other null principals), and therefore does not subsume anything but itself.
### ExpandedPrincipal

## Comparing different types of principals
The Same-Origin Policy defines how to do security checks for two web-like origins, i.e., for principals that have a web-like URL. So, what do we do for those other principals?


## Origin Attributes
- FIXME: link to the nice paper
- FIXME maybe skip and add to a later blog post

## What to consider when you do a load (LoadInfo)


### Further reading
* [nsIPrincipal on MDN](https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Reference/Interface/nsIPrincipal)
* [Principal (computer security) on Wikipedia](https://en.wikipedia.org/wiki/Principal_(computer_security))
* [Script security on MDN](https://developer.mozilla.org/en-US/docs/Mozilla/Gecko/Script_security)



