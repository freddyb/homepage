Title: New CSP directive to make Subresource Integrity mandatory (`require-sri-for`)
Date: 2016-06-02
Author: Frederik


### Background

GitHub is one of the [first big webistes using Subresource Integrity](http://githubengineering.com/subresource-integrity/) and can thus [defend against potentially bad Content Delivery Networks (CDNs)](https://hacks.mozilla.org/2015/09/subresource-integrity-in-firefox-43/).
The tricky thing with SRI is that you have to include it for every HTML tag that points to a CDN if you want the security benefit.
And then, of course, [it happend](https://lists.w3.org/Archives/Public/public-webappsec/2015Dec/0045.html) that someone forgot to add this and people were sad. Fortunately, they brought this to the Webappsec Working Group and discussed the matter!

#### Omitting the details
There have been some discussions whether this should be a parameter on `script-src`, `style-src` etc. that I would like to omit for the sake of brevity. Feel free to jump into the mailing list (linked previously) if you are curious about this.

## How it works
It's simple! Just add the directive into your Content Security Policy and specify if you need this for scripts, styles or both: `Content-Security-Policy: require-sri-for script style`

#### Example:
If you are running today's [Firefox Nightly](https://nightly.mozilla.org/) (June 2nd, 2016), you should not see an alert box from html5sec.org vising this the PHP script below:

```html
<?php
header("Content-Security-Policy: require-sri-for script style");
?>
<!-- This should load but cause a devtools warning because bootstrap requires jquery -->
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js" iintegrity="sha384-0mSbJDEHialfmuBBQP6A4Qrprq5OVfW37PRR3j5ELqxss1yVqOtnepnHVP9aJ7xS" crossorigin="anonymous"></script>

<!-- these shouldn't load and cause a CSP violation to be reported an alert popup indicates failure. -->
<script src="https://html5sec.org/test.js" integrity="foo"></script>
<script src="https://html5sec.org/test.js" integrity=""></script>
<script src="https://html5sec.org/test.js"></script>
```
<small>(Sorry, no public demo URL ☹)</small>


## Calling for testers
This feature is relatively new, so we need some feedback from enthusiasts: Please see if you can find this useful in deployment (looking at you, GitHub folks) and you, security testers: Can you load scripts from other origins without integrity even though a `require-sri-for` policy is in place? But please see my notes on known issues below.

Feel free to look  also into my patch, if you know a thing or two about C++ and Firefox. The implementation was discussed in [Bugzilla bug 1265318](https://bugzilla.mozilla.org/show_bug.cgi?id=1265318) with the patches attached.

## Known Issues
* CSP violation reporting currently complains about the document URL that included the subresource instead of the subresource URL ([bug 1277495]((https://bugzilla.mozilla.org/show_bug.cgi?id=1277495)).
* `<svg:script>` is, *technically speaking*, not the same as HTML's `<script>`, so there are theoretical bypasses via SVG and other mechanisms that run scripts & styles without `<link href>` and `<script src>`. I couldn't bypass this using the obvious svg script tab, but this needs further investigation ([bug 1277248](https://bugzilla.mozilla.org/show_bug.cgi?id=1277248)).
* Firefox doesn't manage to enforce the directive when the CSP is in a `<meta>` tag ([bug 1277557](https://bugzilla.mozilla.org/show_bug.cgi?id=1277557)).
 
## Your Feedback
Please submit your feedback as bugs in [Bugzilla using this link](https://bugzilla.mozilla.org/enter_bug.cgi?product=Core&component=DOM%3A%20Security) if you want someone to see it. I will not monitor IRC, Twitter or E-Mail over the next few months, as I am going to be on leave over the summer.

### Acknowledgements
Thanks to Patrick Toomey from GitHub for raising the issue about SRI enforcement in the first place. Neil Matatall started bringing this into the SRI spec and Sergey Shekyan is currently continuing this. Thanks to the both of you! Thanks to Christoph Kerschbaumer for helping me work on the implementation and Jonathan Hao for doing the [groundwork](https://bugzilla.mozilla.org/show_bug.cgi?id=1235572).
