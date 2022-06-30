# Making of: The Sanitizer API

*This is the full-text version of my conference talk from Nullcon Berlin 2022.
You can also [watch the recording](https://www.youtube.com/watch?v=-f4JP3nwkDo)
or [click through my slides (with speaker notes)](https://docs.google.com/presentation/d/1eLmIZkY7auD8xT-Q6AzBKM_ASFHH8Z5fMyfeoSbSH-k/view)

Sadly, Cross-Site Scripting (XSS) is still a largely unsolved problems.
Despite all of the advice, tooling and mitigations - XSS is still the
most prevalent security vulnerabilities for the better of a decade.

In this article, I want to talk about DOM-based XSS, how I believe
it could be tackled with a Sanitizer that is built right into the browser.
Specifically, we will discuss the design decisions and security considerations
that went into making the currently proposed
[Sanitizer API](https://wicg.github.io/sanitizer-api/).

The Sanitizer API is currently still a draft in the W3C incubation community
group, so it is not fully done or even finished. However, there are prototype
implementations in Firefox and Chrome that we're inviting you to test.


# XSS and `innerHTML`

A simple of DOM-based XSS looks like this and we'll continue using this line of
code in all upcoming examples:

```js
foo.innerHTML = evil;
```

Some attacker-controlled input string `evil` will be assigned to `innerHTML` -
specifically: This assignment will invoke the browser's
[*HTML fragment parser*](https://html.spec.whatwg.org/multipage/parsing.html#parsing-html-fragments),
which is an algorithm that accepts a *context element* (here: `foo`) and turns
the supplied *input* string into a tree representation of html elements and
attributes following the algorithm steps described specifically for that
*context element*.
Afterwards, this tree representation is appended to the *context element* `foo`.

Another interesting thing to note here is that the XSS vulnerability is purely
client-side and that everything happens within the context of the web browser.

To fix those DOM-XSS bugs, many websites make use of a Sanitizer library, like
[DOMPurify](https://github.com/cure53/DOMPurify/).
I believe this is also the most robust approach, even more so when the
Sanitizer can be provided by the browser.


# What is a Sanitizer?

Most sanitizers define a simple string function that accepts bad HTML and return harmless HTML,
like so:

```js
const sanitized = sanitize(evil);
foo.innerHTML = sanitized;
```

The implementation of a Sanitizer can be grouped into the following steps.
1. Parse
2. Sanitize
3. Serialize (optional)

<div><blink><marquee>Insert Image of "What's in a Sanitizer (slide 10)</marquee></blink></div>

Most sanitizers also transform the resulting node tree back to a string, but that's not always the case. This is also called serialization.

All these steps are important here:
Given an example input string of `<p>Hello World!<img src=x onerror=alert(1)>`, it is already
the parser that generates the document fragment and decides how to properly add the closing `</p>` element and how to quote and
terminate the attribute values for `src` and `onerror`.
The sanitizer will then look through the whole node tree and
iterate over the starting element `p`, the `img` element and it's attributes `src` and
`onerror`. Let's assume it will only remove the `onerror` attribute.

Once serialized back into a string, the result should look like
`<p>Hello World!<img src="x" onerror="alert(1)" /></p>`, with all elements closed and
attributes properly quoted.

An important takeaway from this, is that every sanitizer needs to make use of a parser
and that the parser itself may already modify the input. Therefore, I believe that it is
important for the sanitizer to use the parser of the browser that is currently in use.

If a sanitizer does not make use of the existing parser (e.g., through the
[DOMParser API](https://developer.mozilla.org/en-US/docs/DOM/DOMParser)), then there is a risk
of parsing the input incorrectly and misunderstanding what the browser will *actually*
make of the malicious input.
Notably, if an improperly parsed value is then eventually supplied to the document for
additional parsing (e.g, by assigning to `foo.innerHTML`), it will be parsed *differently*.

These kinds of parsing differentials have been a common root cause in many, many different
kind of security vulnerabilities in the last couple of decades.

In this specific case, parsing, re-parsing or misparsing of HTML that leads to XSS has also
been called "Mutated XSS" or just [mXSS](https://en.wikipedia.org/wiki/Cross-site_scripting#Mutated_XSS_%28mXSS%29).

Therefore, it is best to ensure that parsing is done correctly and ideally just once.

# Goals for the Sanitizer API

Our own Sanitizer API should obviously not be prone to mXSS attacks. But there are other
things that we want to provide

- The Sanitizer API defines a notion of "safe HTML". The intent is to provide a baseline of
safe HTML elements and attributes that can and should be reusable for all typical sanitizer
libraries out there. A clear distinction of what is harmless HTML and what isn't will be
useful for the whole ecosystem of XSS solutions.
- The Sanitizer API shoud always be safe by default. No input should allow invoking its
methods in such a way that the resulting HTML is unsafe.
- No parsing mistakes: The Sanitizer API will use the existing HTML parser code.
- Configurable: Developers should be able to use a stricter subset instead of the default configuration

In the end, I hope that a standardized Sanitizer API will be able to shift the responsibility
for dealing with XSS attacks back to the browser.

## The original prototype

The first prototype implementation provided a constructor `new Sanitizer` to create a container for the current configuration. The operation to sanitize a piece of malicious
HTML would then be a function on that object, e.g. `mySanitizer.sanitize()`.


Looking back at the original example, we would be faced with code like this:
```js
let mySanitizer = new Sanitizer();
foo.innerHTML = mySanitizer.sanitize(evil);
```

Given that this `sanitize` function would parse, sanitize and serialize, what would the `innerHTML` assignment do?



P.S:  I'm seeing this presentation as part of a series where I talked about client-side XSS. In 2019, I talked getting [https://frederik-braun.com/firefox-ui-xss-leading-to-rce.html](https://frederik-braun.com/firefox-ui-xss-leading-to-rce.html) by XSSing the interface. In 2020 & 2021, I talked about [Finding & Fixing DOM-based XSS](https://blog.mozilla.org/attack-and-defense/2021/11/03/finding-and-fixing-dom-based-xss-with-static-analysis/) ([Video from JSCAMP 2021](https://www.youtube.com/watch?v=69ntDo5kgN8), [enterJS 2022 Slides](https://docs.google.com/presentation/d/1_FiYfNICK_lA68CaBo7LJZuORl5tkV0R-kVbnozyCFY/edit#slide=id.g25275a8168_0_993)).

