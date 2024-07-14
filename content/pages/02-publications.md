Title: Portfolio
Slug: publications

<!-- chronologically descending order. add on top -->

## Presentations <!-- TODO add PDF/slides -->

* Cross Origin Isolation at OWASP Berlin Meeting - 2024,
[Slides](/publications/cross_origin_isolation_2024.pdf)
* What if XSS was a browser bug? at Hacking in Parallel Berlin - 2022,
[Slides](/publications/what_if_xss_was_a_browser_bug_hip_berlin_2022.pdf)
* Finding and Fixing DOM-based XSS at enterJS Darmstadt - 2022,
[Slides](/publications/enterjs_finding_fixing_domxss_static_analysis_2022.pdf)
* Making of: The Sanitizer API at Nullcon Berlin - 2022: [Video](https://www.youtube.com/watch?v=-f4JP3nwkDo),
[Slides](/publications/making_of_sanitizer_api_nullcon_2022.pdf)
* Fixing Security Bugs in Firefox at Mozilla Berlin All-Hands - 2020
* Remote code execution in Firefox beyond memory corruptions
at OWASP Global AppSec Amsterdam - 2019: [Blog post](https://frederikbraun.de/firefox-ui-xss-leading-to-rce.html),
[Slides](/publications/owasp_appsec_ams_2019_rce_in_firefox_uxss.pdf)
* A CDN that can not XSS you: Using Subresource Integrity
at OWASP AppSec EU, Amsterdam - 2015: [Video](https://www.youtube.com/watch?v=K8ws8qxBJqg), [Blog post](https://frederikbraun.de/using-subresource-integrity.html)
* We're stuggling to keep up - A brief history of browser security
features at JSConf.EU Berlin - 2014: [Video](https://www.youtube.com/watch?v=mj-U9FlbAl0)
* Origin Policy Enforcement in Modern Browsers at OWASP AppSec Research
in Hamburg and at Hack in Paris - 2013: [Paper](/publications/thesis/Thesis-Origin_Policy_Enforcement_in_Modern_Browsers.pdf)


## Projects

* [Sanitizer API](https://github.com/WICG/sanitizer-api), an upcoming standard
that defines built-in HTML/XSS sanitizer primitives for the browser.
* [eslint plugin "no unsanitized"](https://github.com/mozilla/eslint-plugin-no-unsanitized),
a plugin for the popular JavaScript linter that helps finding and fixing
unsanitized HTML interpolation, which could lead to XSS vulnerabilities.
* [Subresource Integrity](https://www.w3.org/TR/SRI/), a W3C specification for
conditionally loading third-party scripts based on their cryptographic digest.
* [Public Suffix List](https://github.com/publicsuffix/list), *the* list that
defines domain suffixes beyond typical IANA top-level domains. (as contributor)
* [eslint plugin "no wildcard postMessage"](https://github.com/mozfreddyb/eslint-plugin-no-wildcard-postmessage),
a plugin for the popular JavaScript linter that disallows usage of the [`postMessage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
API to unspecified end points.
* [discard tab](https://github.com/freddyb/webext-discard-tab), a Firefox
extension that allows unloading a browser tab to disable background activity
and reduce resource usage.
* [html2dom](https://github.com/freddyb/html2dom), a JavaScript library that
rewrites HTML source code into DOM instructions (`createElement`, `appendChild` etc.)

## Blog posts elsewhere

* [Firefox will upgrade more Mixed Content in Version 127](https://blog.mozilla.org/security/2024/06/05/firefox-will-upgrade-more-mixed-content-in-version-127/), with Malte Jürgens, Simon Friedberger, and Christoph Kerschbaumer (June 5, 2024)
* [DOM Clobbering](https://www.htmhell.dev/adventcalendar/2022/12/) (December 12, 2022)
* [Finding and Fixing DOM-based XSS with Static Analysis](https://blog.mozilla.org/attack-and-defense/2021/11/03/finding-and-fixing-dom-based-xss-with-static-analysis/) (November 3, 2021)
* [Examining JavaScript Inter-Process Communication in Firefox](https://blog.mozilla.org/attack-and-defense/2021/04/27/examining-javascript-inter-process-communication-in-firefox/) (April 27, 2021)
* [Understanding Web Security Checks in Firefox (Part 2](https://blog.mozilla.org/attack-and-defense/2020/08/05/understanding-web-security-checks-in-firefox-part-2/)) (August 5, 2020)
* [Hardening Firefox against Injection Attacks – The Technical Details](https://blog.mozilla.org/attack-and-defense/2020/07/07/hardening-firefox-against-injection-attacks-the-technical-details/) (July 7, 2020)
* [Understanding Web Security Checks in Firefox (Part 1)](https://blog.mozilla.org/attack-and-defense/2020/06/10/understanding-web-security-checks-in-firefox-part-1/) (June 10, 2020)
* [Help Test Firefox’s built-in HTML Sanitizer to protect against UXSS bugs](https://blog.mozilla.org/attack-and-defense/2019/12/02/help-test-firefoxs-built-in-html-sanitizer-to-protect-against-uxss-bugs/)(December 2, 2019)
* [Remote Code Execution in Firefox beyond memory corruptions](https://blog.mozilla.org/attack-and-defense/2019/09/29/remote-code-execution-in-firefox-beyond-memory-corruptions/) (September 29, 2019)

## Papers

* [Hardening Firefox against Injection Attacks (PDF)](/publications/hardening_paper.pdf), with Christoph Kerschbaumer, Tom Ritter; SecWeb - Designing Security for the Web; Genova, Italy, September 2020
* [X-Frame-Options: All about Clickjacking?](/xfo-clickjacking.pdf)
Whitepaper together with Mario Heiderich, Fall 2013
* [Origin Policy Enforcement in Modern Browsers](/publications/thesis/Thesis-Origin_Policy_Enforcement_in_Modern_Browsers.pdf),
Diploma thesis, Summer/Fall 2012.
[Errata (TXT)](/publications/thesis/errata.txt), Test Cases/Appendix available on request.
