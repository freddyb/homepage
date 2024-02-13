Title: How Firefox gives special permissions to some domains
Date: 2024-02-02
Author: Frederik
Slug: special-browser-privileges-for-some-domains
tags: websecguide

Today, I found someone tweeting about a neat [security bug in Chrome, that
bypasses how Chrome disallows extensions from injecting JavaScript into
special domains like `chrome.google.com`](https://crbug.com/1472898).
The intention of this block is that browsers give special permissions to
some internal pages that allow troubleshooting, resetting the browser,
installing extensions and more.

The bug in question was an easy bypass of a domain block list due to a DNS
trick. Due to a strict host name match, an attacker could extend the current
hostname with a trailing dot to `chrome.google.com.` and bypass the block.

I believe, this allowed all extensions that can inject content scripts into
arbitrary domains to potentially make use of these extra privileges.

Of course, this got me thinking. What if we have this bug in Firefox too?
So I went on and looked at our code. Fortunately, I have been playing with
our permission system for quite a while already, so I knew what to do.

First of all, Firefox uses a so-called PermissionManager API, which gets
its default values from the file
[browser/app/permissions](https://searchfox.org/mozilla-central/rev/14dc8f0e748d44778a02ffcf9ebcda3851b2bf9e/browser/app/permissions)
in the source tree. At the time of writing this article, the four different
possible permissions are `uitour`, `install`, `remote-troubleshooting` and
 `autoplay-media`. So far, I have only looked into the first two, as I know
 how they work and what they do. But for the purpose of this analysis, and
 due to all of them going throgh the
 [PermissionManager](https://searchfox.org/mozilla-central/source/netwerk/base/nsIPermissionManager.idl#47),
 I am relatively confident that testing two of those should verify the
 behavior of the API in itself - regardless of the specific permissions and
 sites involved.

The `install` permission is used on `addons.mozilla.org` to allow the website
to trigger the installation of Firefox extensions. In fact, you can test that
this is the case by navigating to `addons.mozilla.org` and looking at the
exposed interfaces: `typeof AddonManager` returns `"function"`.
However, on any other web page, the result of that expression is `undefined`.

Now that we know how to test whether a page has the `install` permission, we
can open tab that goes to `addons.mozilla.org.` and do the same again.
What's `typeof AddonManager` here? `undefined`. No dice.

Let's continue with the `uitour` permission.
The `uitour` permission is used in Firefox's new tab, support and download
pages. It is used to invoke functionality from the user interface.
When a Firefox user is being presented new features after a major upgrade,
the `uitour` events can highlight Firefox menu buttons or open popups that
contain new funcionality.

A specific example that I remember is that for example, when a Firefox user
tries to download a new Firefox package, we assume that they are confused or
dissatisfied with how their browser is setup right now. So instead of
offering a download file, we also suggest "refreshing" Firefox, which can
help undo some undesired customizations without losing stored passwords
and such.

The code that you can run to try the `uitour` feature on `www.mozilla.org`
is as such:

```js
document.dispatchEvent(new CustomEvent('mozUITour', {
    bubbles: true,
    detail: {
        action: 'resetFirefox',
        data: {
        }
    }
}));
```

Dispatching this event will get you a new impressive modal dialog that asks
the user if they really want to refresh Firefox.

Now that we have a test for the `uitour` feature, we can do the same thing
we tried last time: Add a trailing dot and try again.

Going to `www.mozilla.org.` and trying again yields similar results as above:
No prompt shows.

To summarize: Our quick analysis has shown that even if we could get the web
extension code to be confused about whether a page should be scripted. The
 permission manager does not play along.

I think we can safely assume that Firefox is not affected by the same bug.
But you shouldn't take my word for it. Feel free to prove me wrong:
Here are some links to our code:

- [AddonManager API code](https://searchfox.org/mozilla-central/source/toolkit/mozapps/extensions/AddonManagerWebAPI.cpp#84)
- [AddonManager Interface](https://searchfox.org/mozilla-central/source/dom/webidl/AddonManager.webidl#60)
- [Code search for additional uitour event examples](https://searchfox.org/mozilla-central/search?q=_sendEvent&path=uitour&case=false&regexp=false)

If you feel like you have found something that I did not, please submit to the
[Firefox bug bounty program](https://www.mozilla.org/en-US/security/client-bug-bounty/).
