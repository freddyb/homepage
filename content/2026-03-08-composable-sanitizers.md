Title: Composing Sanitizer configurations
Date: 2026-03-08
Slug: composable-sanitizers
Author: Frederik

The HTML Sanitizer API allows multiple ways to customize the default allow list
and this blog post aims to describe a few variations and tricks we came up with
while writing the specification.

## Safe and unsafe Configurations

Examples in this post will use configuration dictionaries.
These dictionaries might be used in safe methods like `Element.setHTML()`
and `Document.parseHTML()`, but also its unsafe counterparts
`setHTMLUnsafe()` and `parseHTMLUnsafe()`. The behavior is subtly different,
as the unsafe variants can take a provided config verbatim and will just run
with it.

The safe methods will make sure that any provided configuration does not
re-introduce security issues, as there is supposed to be NO WAY to configure
the Sanitizer API into Cross-Site Scripting (XSS)

## `removeUnsafe()`

The `removeUnsafe()` operation is a function on the Sanitizer global and makes
sure that a config is indeed completely safe. The browser will run
`removeUnsafe` internally when a custom configuration is provided to a safe
method. The steps to remove unsafe essentially make sure that no known event
handler attributes or script elements are allowed. It will also remove links
(`href` attributes) pointing to `javascript:` URLs.

## Default Sanitizer / Empty Sanitizer

By default, `setHTML()` will allow much more than scripts. This is to help with
unexpected styling, spoofing, phishing, redirects or script execution in a
different origin (e.g., with `<iframe>`s).

Users of the Sanitizer API that want XSS protections but nothing more can supply
an empty sanitizer config `{}` to a safe method. Just providing this dictionary
will suffice to allow everything and remove nothing besides scripts

## Allow lists

Typical security advice is to think of what you want to allow upfront and
enumerate all the desired output. A typical forum or comment field migt use this:

<code>
{
  elements: ["p", "i", "em", "b", "s", "ul", "ol", "li", "blockquote", "code", "strong"],
}
</code>

This would allow the aforementioned elements and provide a robust
guarantee that whatever HTML elements will be invented in the future are not
suddenly messing with your layout.

## Deny lists

People that want to allow all sorts of HTML except scripts and then *some*, can
use a deny list. The downside is that this list won't be as future proof and
upcoming additions to HTML might violate your assumptions about what is and is
not allowed. On the flipside, if you *do* want to allow almost everything, you
can make sure that future HTML features are going to work without additional
code changes.

## Modyfing and composing Sanitizer configurations

The Sanitizer API also provides methods on the `Sanitizer` object to modify
any given configuration.

The following methods will essentially do exactly what their names suggests:

* `allowAttribute()`: Add additional attribute to be allowed.
* `allowElement()`: Allow another element.
* `get()`: Return the current configuration as JSON.
* `removeAttribute()`: Remove an attribute.
* `removeElement()`: Remove an element.
* `removeUnsafe()`: Remove known XSS elements, attributes and attribute values.
* `replaceElementWithChildren()`: Replace an element with its children
(useful to remove `<a>` but keeping the inner text).
* `setComments()`: Pass a boolean to say whether comments should be stripped
* `setDataAttributes()`: Pass a bool to say whether `data-` attributes are allowed.

## Composable Sanitizers

The main upside of the modification methods is that Sanitizers can be provided
for a specific context: A framework may say that some specific data attributes
must not be used and developers can use the `frameworkSanitizer` and remove
additional undesirable content on top of the given configuration.
