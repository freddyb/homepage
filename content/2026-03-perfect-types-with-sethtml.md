Title: Perfect types with `setHTML()`
Date: 2026-03-07
Slug: perfect-types-with-sethtml
Author: Frederik

**TLDR: Use `require-trusted-types-for 'script'; trusted-types 'none';` in your
CSP and nothing besides `setHTML()` works, essentially removing all DOM-XSS risks.**

## Background: Sanitizer API

I was guest at the [ShopTalkShow Podcast](https://shoptalkshow.com/704/)
to talk about `setHTML()` and the HTML Sanitizer API. Feel free to listen to the
whole episode, if you want to take it all in. It's a great introduction.

Meanwhile, MDN has a good explanation of the [`Sanitizer`](https://developer.mozilla.org/en-US/docs/Web/API/Sanitizer/Sanitizer)
constructor to create a custom configuration and
[`Element.setHTML()`](https://developer.mozilla.org/en-US/docs/Web/API/Element/setHTML)
as the main entry point of the API.
People who do not want to directly insert into the document can also create a
new document with
[`Document.parseHTML()`](https://developer.mozilla.org/en-US/docs/Web/API/Element/setHTML).

## Trusted Types

Trusted Types (<abbr>TT</abbr>) is a feature in
[Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
(<abbr>CSP</abbr>),
that can help prevent DOM-based XSS. By enabling "trusted types" in your CSP,
with a policy like so `require-trusted-types-for 'script'; trusted-types 'mypolicy'`,
scripts will
not be able to start HTML parsing/insertion from normal strings (e.g.,
through `document.write()`, `innerHTML=` and so on).
These so-called <i>HTML parsing sinks</i> will now only accept `TrustedHTML`
objects - hence the name trusted.
Creating these types is ideally controlled with a so-called
[TrustedTypePolicy](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API#the_trusted_types_javascript_api)
that is also allowed per the header (`mypolicy` in the example above).

I would argue that the creation and maintenance of policy code will require
constant vigilance and maintenance by security-minded people. It is possible,
but not something I would require of every web developer.

## Perfect Types

This leads us to Perfect Types. The idea of so-called Perfect Types is that
**no** policy is allowed. The following header both requires that the legacy
HTML parsing APIs all require Trusted Types but also that no policy exists
to ever create them:

`require-trusted-types-for 'script'; trusted-types 'none';`.

With this policy, your only way to safe HTML modification is by using the new
safe methods:

1. Use `setHTML()` to directly insert into your document
2. Use `Document.parseHTML()` to insert into a temporary document, select your
desired piece of context (e.g., with `querySelector`) and then use `cloneNode`
or other `Node` APIs to move the elements into your current document.

## Acknowledgements

This idea is heavily inspired by a great idea from
[Jun Kokatsu](https://www.linkedin.com/in/shhnjk) and his
[blog post about "Perfect Types"](https://microsoftedge.github.io/edgevr/posts/eliminating-xss-with-trusted-types/).
He didn't suggest using `setHTML()`, because it didn't exist yet. Instead, he
described using Perfect Types to disallow the DOM XSS sinks and then relied on
React to take care of the safe HTML modification.
