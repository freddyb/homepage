Title: Reference Sheet for Principals in Mozilla Code
Date: 2020-08-03
Slug: principals-reference.md
Author: Frederik

Note: This is the *reference sheet* version.
The details and the big picture are covered in [Understanding Web Security Checks in Firefox (Part 1)](https://frederik-braun.com/understanding-web-security-checks-in-firefox-part-1.html).

# Principals as a level of privilege
A security context is always using one of these four kinds of Principals:

* **ContentPrincipal**: This principal is used for typical web pages and can be serialized to an origin URL, e.g., https://example.com/.

* **NullPrincipal**: Some pages are never same-origin with anything else. E.g., `<iframes sandbox>` or documents loaded with a data: URI. The standard calls this an [opaque origin](https://html.spec.whatwg.org/multipage/origin.html#concept-origin-opaque).

* **SystemPrincipal**: The SystemPrincipal is used for the browser's user interface, commonly referred to as "browser chrome". Pages like `about:preferences` use the SystemPrincipal.

* **ExpandedPrincipal**: A browser extension is more privileged than normal web pages, but must also be able to assume the security context of a website. Hence, an ExpandedPrincipal is best understood as a list of principals to match the security needs for Content Scripts in Firefox Extensions. The security checks on the ExpandedPrincipal are then implemented as a loop through this allowlist of principals.

# Principals to be considered during security checks
* **loadingPrincipal**: The principal of the document where the result of the load will be used.

* **triggeringPrincipal**: The security context that actually triggered the URL to load. In most cases the loadingPrincipal and the triggeringPrincipal are identical. But imagine a cross-origin CSS resource loading a background image. Here, the triggeringPrincipal is principal for the CSS file.


As an aside: There's also a **[StoragePrincipal](https://searchfox.org/mozilla-central/source/toolkit/components/antitracking/StoragePrincipalHelper.h#13)**: To adjust anti-tracking settings in Firefox, we can change the Principal that a document is using for storage (and related technologies) on the fly. This is achieved with a StoragePrincipal.
