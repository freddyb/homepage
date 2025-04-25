Title: The _S_ in interoperability
Date: 2025-04-23
Author: Frederik

This is a blog post about standards, their proliferation and the issues
that may arise.
My first involvement with standards was just as a reader. To
better understand complicated code or unexpected behavior in a protocol.
After a while, I also got involved and helped clarify certain things to ensure
implementations align on the same behavior in edge cases.
Eventually, I found myself [co-editing a specification](https://www.w3.org/TR/SRI/)
which was adopted by all browsers out there.

I learned a lot from this work. It's quite humbling, when
you learn where something as simple as matching a cryptographic digest to a URL
can be ambiguous. The standard format is sha386-base64-encoding-of-the-hash.
Whereas the typical hex encoding is rather straightforward, base64 comes in two
encoding alphabets. First, `a-zA-Z0-9/+` and secondly the url-safe variant
which uses `a-zA-z0-9_-`. We found a major browser liberally accepting both
types of encoding, because people often time use base64 and base64url
interchangably. This resulted in all browsers accepting both types of encoding
in order to ensure site compat in all browsers.

# When a specification becomes a standard

The main difference between a specification and a standard is adoption.
A specification is at first just a write-up from someone about something.
How it should behave, how it works, what the data structures, the algorithms
and the interactions of them look like. Anyone can come up with a grammar,
a parser and a resulting data structure.
But it takes more than a write-up to form a standard.

For a standard, the specification must be widely implemented and universally
understood as the same thing. This will work best with iterative co-design of
the spec, the implementations and intense dicsussions of the corner cases.
Some may go further and use [shared test suites](https://github.com/web-platform-tests/wpt/),
ideally even allowing formal verification.

But sometimes, syntax is deceivably simple to parse without reading the spec:
People have written parsers for text-based languages. You may know the post
about [parsing HTML
with regular expressions](https://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags).
Other great examples of "easily" parsed languages are maybe XML, JSON, or YAML.

# What is interoperability?

Interoperability (interop) is what sets aside the specification from a
standard. When something is universally understood, implemented and behaves the
same across multiple languages, frameworks and libraries - only then it becomes
a true interoperable standard.

Despite a lot of effort, interoperability is more of a path than a destination,
as it requires constant maintenance and observation of the ecosystem beyond an
individual implementation.

I would go so far and consider interoperability asymptotic. There's gradual
convergence towards full interop, but it may never be fully reached.

# Postel's Law

Most of the time, gradual interop is fine. After all,The internet was built
on [rough concensus and running code](https://www.ietf.org/participate/).
People were told to "be conservative in what you do, be liberal
in what you accept from others". This, also known as Postel's Law or the
[robustness principle](https://en.wikipedia.org/wiki/Robustness_principle) and
it has served the internet really well in getting separate implementations
working with each other.

In contrast to that, the presentation by Meredth L. Patterson and Sergey Bratus on [The Science
of Insecurity](https://www.youtube.com/watch?v=3kEfedtQVOY) and what they
call [Language-theoretic Security (langsec)](http://www.langsec.org/),
already calls for stricter formal standards with rigurous parsing and
error rejection, rather than ad-hoc recognition that accepts all
sorts of variants and abmiguities.

The The IETF's Internet
Architecture Board (IAB) has also acknowledged this and released
[RFC 9413 on Maintaining Robust Protocols](https://intarchboard.github.io/draft-protocol-maintenance/draft-iab-protocol-maintenance.html)
in 2023:
As a call for active maintenance and reduced ambiguity, it directly mentions
that accepting and parsing unexpected input data "is no longer considered
best practice" (Ibid.).

# Parser Differentials

As an example, parsing JSON has been known to be a proverbial [minefield](https://seriot.ch/projects/parsing_json.html)
since at least 2016. Let's examine this JSON string and the resulting data structure:

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
Another one might check for existance
and reject the second `"test"` key silently, keeping the first one.
Given the lack of rigor in the original description of JSON as a
"subset of JavaScript" was already acknowledged and raised as problematic
in the JSON RFC (which came much later in 2017).
Still to this day, most JSON libraries allow input with duplicate dictionary
keys.

If you just keep going with the very specific and limited case of dictionary
parsing, you will find that the same is not only an issue for JSON, but also
YAML, HTML, XML (attributes on an element are often stored in a dictionary),
CBOR, [Structured Field values for HTTP](https://httpwg.org/specs/rfc8941.html)
and many more.

In fact, these issues are widely known and can still lead to catastrophic
issues in 2025:

* **YAML**: [parsing bug leading to an arbitrary file-write on
GitLab](https://gitlab-com.gitlab.io/gl-security/security-tech-notes/security-research-tech-notes/devfile/)
found by Joern Schneeweisz in 2024
* **JSON**: 2024 ASIA CCS paper on
[Cross-Language Differential Testing of JSON Parsers](https://www.mlsec.org/docs/2024b-asiaccs.pdf)
by Jonas Möller, Felix Weißberg, Lukas Pirch, Thorsten Eisenhofer, and Konrad Rieck
* **XML**: A bug in ruby-saml [allowed bypassing popular Single-Sign-On (SSO)
consumers](https://github.blog/security/sign-in-as-anyone-bypassing-saml-sso-authentication-with-parser-differentials/)
by Peter Stöckli

# What do we learn from this?

I don't know. Software is shit?
