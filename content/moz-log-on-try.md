Title: logging with MOZ_LOG on the try server
Date: 2018-12-11
Author: Frederik
Slug: moz-log-on-try

# Preamble

NB: This is mostly for my own public reference. I had written about this
elsewhere in 2016 but when arriving at a similar problem, failed to
reproduce this. You may skip the following section, if you're familiar
the terminology in the title

## what is MOZ_LOG?
`MOZ_LOG` is an environment variable Firefox developers can use to tell
specific code sections to emit verbose (or very verbose) status messages
for some if its inner workings. This is also called
[Gecko Logging](https://developer.mozilla.org/en-US/docs/Mozilla/Developer_guide/Gecko_Logging)

## what is the try server
The [try server](https://firefox-source-docs.mozilla.org/tools/try/index.html)
is a repository that allows you to submit code without actually checking it
into the public repository. Pushes to try get run through all of our tests,
which helps identifying problems and test failures before they are part of
our code.


# logging with MOZ_LOG on the try server

There is a test failure on Mac OS X, that I can hardly debug.
As a first step, I'll push this to the try-server with more logging
output enabled.

My test is a mochitest, so I modified testing/mochitest/runtests.py:

```
diff --git a/testing/mochitest/runtests.py b/testing/mochitest/runtests.py
index 45545b4..5afdffd 100644
--- a/testing/mochitest/runtests.py
+++ b/testing/mochitest/runtests.py
@@ -91,7 +91,7 @@ here = os.path.abspath(os.path.dirname(__file__))
 # Try run will then put a download link for all log files
 # on tbpl.mozilla.org.

-MOZ_LOG = ""
+MOZ_LOG = "nsDocShellLogger:4,CSPParser:4,CSPUtils:4,CSPContext:4,CSP:4"
```

And now we play the waiting game.
