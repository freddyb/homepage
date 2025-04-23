Title: The _S_ in interoperability
Date: 2025-04-23
Author: Frederik

I have been thinking about standards for a very long time. At first as a way to
better understand complicated code or unexpected behavior in a protocol.
After a while, I also got involved and helped clarify certain things or ensure
implementations align on the same behavior in error cases.
Eventually, I found myself [co-editing a specification](https://www.w3.org/TR/SRI/)
which was adopted by all browsers out there.

I learned a lot from this work. It's quite humbling, when
you learn that something as simple as matching a cryptographic digest to a URL
can be ambiguous.

# When a specification becomes a standard

The main difference between a specification and a standard is adoption.
A specification is not more than a write-up from someone about something.
How it should behave, how it works, what the data structures, the algorithms
and the interactions of them look like. Anyone can come up with a grammar,
a parser and a resulting data structure.
But it takes more than a write-up to form a standard.

For a standard, this specification must be widely implemented and universally
understood as the same thing. This will work best with iterative co-design of
the spec, the implementations and intense dicsussions of the corner cases.

Sometimes, syntax is deceivably simple to parse without reading the spec:
People have written parsers for text-based languages like [parsing HTML
with regular expressions](https://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags),
when there are in fact many [idiosyncrasies of the HTML parser](https://htmlparser.info/).
Other great examples of easily misparsed languages are maybe XML, JSON, or YAML.

# What is interoperability?

Interoperability it what sets aside the specification from a standard. When
something is universally understood, implemented and behaves the same across
multiple languages, frameworks and libraries - only then it becomes a true
interoperable standard.

Despite a lot of efforts, interoperability is more of a path than a destination,
as it requires constant maintenance and observation of the ecosystem beyond an
individual implementation.

I would go so far and consider interoperability asymptotic. There's gradual
convergence towards full alignment, but it may never be fully reached.

# Postel's Law

The internet was built based on [rough concensus and running code](https://www.ietf.org/participate/).
When in doubt, people were told, to "be conservative in what you do, be liberal
in what you accept from others". This, also known as Postel's Law or the
[robustness principle](https://en.wikipedia.org/wiki/Robustness_principle), has
served the internet well in getting things off the ground.

However, this principle has long since been superseded. The IETF's Internet
Architecture Board (IAB) has already ratified
[RFC 9413 on Maintaining Robust Protocols](https://intarchboard.github.io/draft-protocol-maintenance/draft-iab-protocol-maintenance.html):
As a call for active maintenance and reduced ambiguity, it directly mentions
that accepting and parsing unexpected input data "is no longer considered
best practice" (Ibid.).

Similar, in their presentation from the 28th Chaos Communication Congress 2021 in
Berlin, Meredth L. Patterson and Sergey Bratus on [The Science
of Insecurity](https://www.youtube.com/watch?v=3kEfedtQVOY) and what they
call [Language-theoretic Security (langsec)](http://www.langsec.org/).
In essence, they **also** call for formal standards with strict parsing and
error rejection, rather than ad-hoc parsing that accepts abmiguities.

# Parser Differentials

Parsing JSON has been known to be a proverbial [minefield](https://seriot.ch/projects/parsing_json.html)
since at least 2016. Let's examine this JSON string and the resulting data structute:

```json
{
    "test": 0,
    "test": 1
}
```

When parsed into an object `obj`, what do you think will `obj.test` return?
Most JSON parsers are so liberal that they will happily consume two dictionary
keys with the same name `"test"`. One implementation may simply assign `obj.test`
twice, first with `0` and then with `1`. Another one might check for existance
and reject the second `"test"` key silently, keeping the first one.
I have not tested this in 2025, but I know in 2016, it was trivial to find to
implementations that would contradict each other.

If you just keep going with the very specific and limited case of dictionary
parsing, you will find that the same is not only true for JSON, but also YAML,
HTML, XML (attributes on an element are often stored in a dictionary),
CBOR, [Structured Field values for HTTP](https://httpwg.org/specs/rfc8941.html)
and many more.

In fact, the bugs with these formats are endless.

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
