Title: Week 29 2013
Date: 2013-07-21
Slug: 2013-wk-29
Author: Frederik

In our Security Disaster of the Week, H. Marco and Ismael Ripoll found
out that *all* applications statically linked and compiled via glibc
since 2006 have their pointers protected by being
[XORed with zero](http://hmarco.org/bugs/CVE-2013-4788.html).
Exploit mitigation at its finest.


My favorite type of browser vulnerability remains the
good old Same-Origin Policy (SOP) bypass: Usually the SOP enforces a
virtual boundary in which web sites are allowed to include content from
other domains (scripts, displaying images) but prevented from accessing
the actual content. If the SOP is bypassed, your gmail inbox leaks. A
good example is 
[Armin Razmdjou's](http://www.rawsec.net/wmp-vulnerability.html) finding:
Attackers can abuse a playlist API in the Windows Media Player browser plugin to
read contents from arbitrary web pages. Specifying a URL within the same
origin that redirects to the interesting site will satisfy WMP's SOP.
Reading the playlist's content then reveals the HTML source code. Tada!


Zane Lackey and Omar Ahmed of the Etsy Security Team
[analysed SSL traffic](http://codeascraft.com/2013/07/16/reducing-the-roots-of-some-evil/)
to see which CAs are actually required in their day to day business.
Their data could be used to reduce the set of trusted CAs to a minimum.


Matt Wobensmith of Mozilla's QA started submitting code to the [Content Security
Policy (CSP) test suite](http://webappsec-test.info/) for the W3C Web Application Security Working Group, Thanks!
