Title: Security Review: HTML sanitizer in Thunderbird
Date: 2013-07-22
Slug: secreview-750436
Author: Frederik

I spent a few days working on a [security review for
Thunderbird's HTML sanitizer](https://bugzilla.mozilla.org/show_bug.cgi?id=750436).
Thunderbird has three presets for viewing mail: Original HTML, Simple
HTML, and Plain Text. No matter which preset the user prefers, emails
should not execute JavaScript. And this is where the HTML sanitizer
joins our party.

This security review was discussed in one of my first weeks at Mozilla
and though being [a very interesting topic](https://bugzilla.mozilla.org/show_bug.cgi?id=704482), it soon occured to me that
I might have bitten off more than I could chew. So the security review got
stuck in my queue and I finally dared to take a stab at it months later.
(Thanks to those fellow Mozillians who helped me getting started!)

#### The key lesson about HTML sanitizers is: Don't even consider writing your own.

So without further ado, I started collecting bits and pieces together.
First I required [creating a recent build of Thunderbird](https://developer.mozilla.org/en-US/docs/Simple_Thunderbird_build). Then I looked into [XPCShell tests](https://developer.mozilla.org/en/docs/Writing_xpcshell-based_unit_tests)
(unit tests using Mozilla's privileged JavaScript libraries) and the [nsIParserUtils interface](https://developer.mozilla.org/en-US/docs/XPCOM_Interface_Reference/nsIParserUtils#sanitize).
My next step was writing a basic sanitizer call, and it turned out comparably
easy:

```js
var ParserUtils =  Cc["@mozilla.org/parserutils;1"].getService(Ci.nsIParserUtils);
var sanitizeFlags = ParserUtils.SanitizerCidEmbedsOnly|ParserUtils.SanitizerDropForms|ParserUtils.SanitizerDropNonCSSPresentation;
var output = ParserUtils.sanitize("XXX HTML here", sanitizeFlags);
```

With this prototype, I could easily loop around a dataset of HTML vectors.
For this I chose the vectors from the [html5 security cheat sheet](http://html5sec.org)
and [RSnake's old XSS cheat sheet](http://ha.ckers.org/xss.html)
(thank you guys!)

Thankfully the html5 security cheat sheet has its attacks in a
[JSON file](http://html5security.googlecode.com/svn/trunk/items.json).
Extracting them was as easy as taking this dataset and joining the vectors
with the file that contains the actual attack [payload](http://html5security.googlecode.com/svn/trunk/payload.json),
(i.e., JavaScript alerts and other triggers in various encodings). The
XPCShell comes with a `load()` function which makes it very easy to include these JSON files.

The full test then looks a bit like this:
```js
var Ci = Components.interfaces;
var Cc = Components.classes;

// gives us an items object:
load("html5sec_items.js");
// possible payloads for within those vectors (items[x].data)
load("html5sec_payloads.js");

// from html5sec.org's import.js:
for (var item in items) {
// replace the payload templates
  for (var payload in payloads) {
    var regex = new RegExp('%' + payload + '%', 'gm');
    items[item].data = items[item].data.replace(regex, payloads[payload]);
    if (items[item].attachment && items[item].attachment.raw) {
      items[item].attachment.raw = items[item].attachment.raw.replace(regex, payloads[payload]);
    }
  }
}
// initialize parser object
var ParserUtils =  Cc["@mozilla.org/parserutils;1"].getService(Ci.nsIParserUtils);
var sanitizeFlags = ParserUtils.SanitizerCidEmbedsOnly|ParserUtils.SanitizerDropForms|ParserUtils.SanitizerDropNonCSSPresentation;

for (var item in items) {
  // sanitize vector
  var out = ParserUtils.sanitize(items[item].data, sanitizeFlags);
  items[item].sanitized = out;
}

// results for html5sec cheat sheet
var mini_items = items.map(function(e) { return {data:e.data, sanitized:e.sanitized}; });

load("xss_rsnake.js"); // array of rsnake xss cheat sheet entries
rsnake_results = [];
for (var i in xss_rsnake) {
  var out = ParserUtils.sanitize(xss_rsnake[i], sanitizeFlags);
  rsnake_results.push({"data": xss_rsnake[i], "sanitized": out});
}
collected_results = mini_items.concat(rsnake_results);
dump(JSON.stringify(collected_results)); // full output as JSON

// html-strings to stdout:
for (var i of collected_results) {
  dump(i.sanitized);
}
```

After sanitizing all of these attack vectors, I had to review the
results. Since this is my first dive into XPCShell tests, I didn't dare
to hook all the logic behind script parsing, image loading, event
handler registration and so forth. Instead I reviewed the sanitized
output by hand (a [JSON capable editor](http://jsoneditoronline.org/)
helps a lot). After that I also put the combined output into a single HTML
file and opened it in the browser. The Firefox Developer Console
helped me confirm that no resources were loaded and no scripts executed.

This means that the sanitizer successfully stripped all the scripts
tags, self-submitting forms and event handlers:
Security Review done!

<small>For convenience, I have uploaded my test results as a JSON file. It is
an [array of objects](http://pastebin.mozilla.org/2648340) in the format `{"data": "...", "sanitized": "..."}`.</small>
