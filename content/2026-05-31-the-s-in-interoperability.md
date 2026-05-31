Title: The S in interoperability
Date: 2026-05-31
Author: Frederik

This is a blog post about standards, their proliferation and the issues
that may arise.
My first involvement with standards was just as a reader. To
better understand complicated code or unexpected behavior in a protocol.
After a while, I also got involved and helped clarify certain things to ensure
implementations align on the same behavior in edge cases.
Eventually, I found myself co-editing a specification -
[Subresource Integrity](https://www.w3.org/TR/SRI/) (SRI) which was published as
a W3C Recommendation in 2015. The core idea behind SRI is that you include
third-party JavaScript combined with a SHA2 digest of the expected file.
If the browser does not find the downloaded URL to match the expected digest,
the script will not execute. This allows using a fast CDN for JavaScript
without giving them full control over the scripts on your page - essentially
reducing the security risks.

The standard format for these digests is e.g.,
`sha(size)-(base64 encoding of the digest)`.
While computing the hash digest is rather straightforward, base64 comes in two
encoding alphabets: First, `a-zA-Z0-9/+` and secondly the url-safe variant
which uses `a-zA-z0-9_-`. The specification examples all used the former.

Only approximately ten years after publication, in 2025, we still found a bug.
As part of a compatibility report against Firefox not properly supporting a
website, we found that the core issue was actually with a different browser.
The other browser liberally accepted both types of encoding, which resulted in
websites expecting support for base64 and base64url interchangeably.
The page did not work in Firefox, because it did not accept all hashes a
website wanted the browser to check, revealing a minor security issue.

The real fix would have been that the standard clarifies that
the base64url variant is incorrect and the other browser engine changes
their behavior.

But due to (somewhat unrelated) issues around proliferation of standards, web
compatibility and the unfortunate market dominance of certain browsers, we
went the other road. To support existing web content, we changed the standard
to acknowledging that both types of encoding are considered valid
representations.

This example shows, that it can take multiple years for subtle differences to
appear. Interoperable specifications can establish a shared
understanding along a "happy path", but not necessarily in adversarial
settings. In addition, standards need to continuous maintenance and active
stakeholders who ensure that implementations remain interoperable and secure
over time.

# From specification to standard

Originally, a specification is at first just a write-up, an idea how something
could be better:
How it should behave, how it works, what the data structures, the algorithms
and the interactions of them look like. Anyone can come up with a grammar,
a parser and a resulting data structure.

For a standard, this specification needs a shared agreement that is also
widely and consistently implemented. This will work best with iterative
co-design of the spec, the implementations and intense discussions of
corner cases.
Some may go further and use [shared test suites](https://github.com/web-platform-tests/wpt/).

This will lead to Interoperability (interop), but still
requires constant maintenance and observation of the ecosystem beyond
individual implementations. While interop is asymptotic and requires a shared
agreement over time, security demands **understanding** - a broader reach that
requires the inspection of limitations and subtle boundaries.

This deeper level of understanding is often missing when implementations
consider syntax "simple enough" without reading the spec. The base64 SRI example is just one example, but there are more:

Many people have written their own parsers for text-based
languages. You may have seen code that parses HTML with regular expressions.
Other great examples of "easily" parsed languages are maybe XML, JSON, or YAML.

But these implementations often make different assumptions, leading to subtle incompatibilities or even security flaws.

# Parser Differentials

More practical, let's look at an issue with JSON, to demonstrate the impact of
handling input that is ostensibly simple.
Let's examine this JSON string and the resulting data structure:

```json
{
    "test": 0,
    "test": 1
}
```

When parsed into an object `obj`, what do you think will `obj.test` return?
Most JSON parsers are so liberal that they will happily consume two dictionary
keys with the same name `"test"`. One implementation may simply assign `obj.test`
twice: First with `0` and then overwrite it with `1`.
Another one might check for existing keys
and reject the second `"test"` key silently, keeping the first one.

The lack of rigor in the original description of JSON as a
"subset of JavaScript" was already acknowledged and raised as problematic
in the JSON RFC (which came much later in 2017).
But still to this day, many implementations allow input
with duplicate dictionary keys and show divergent behavior.

While the examples with SRI and JSON are relatively harmless, real
parser differential bugs were leading to code execution,
authentication bypasses and more[^1].

# What do we learn from this?

Perfect interoperability is not created through a specification, it needs
constant maintenance. The ambiguity can only be removed through long-term
commitment and regular feedback from implementations and users.

The same is true for security: The SRI bug persisted for ten years and
nobody noticed how implementations disagreed and corner cases were overlooked.
They only aligned due to a real, user-facing issue.

But these examples are not a warning sign, they are scar tissue that shows how
the internet is made. Standards can only mature through vigilant maintenance.

The bug reports, the spec issues being filed, the shared test
cases, sometimes even the random forum complaints. All of these help to
remove ambiguity and allow internet standards to mature.

In the end, standards are not secure because they are written down. They are secure because people continue to question, understand, and maintain them.

 [^1]: [JSON](https://seriot.ch/security/parsing_json.html), [YML](https://gitlab-com.gitlab.io/gl-security/security-tech-notes/security-research-tech-notes/devfile/), [XML](https://github.blog/security/sign-in-as-anyone-bypassing-saml-sso-authentication-with-parser-differentials/), [and more](https://www.youtube.com/watch?v=Dq_KVLXzxH8)
