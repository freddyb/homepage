Title: Firefox OS apps and beyond
Date: 2016-04-12
Author: Frederik

I have written two Firefox OS apps, which are both not very popular. You may stop reading here if you haven't used either *squeezefox* or *wallabag-fxos*. This article is about how I think they should evolve, while [Firefox OS is currently transitioning into a community-led B2G OS.](https://wiki.mozilla.org/SmartPhone_Code_Transition)

The apps I have written are both simple web clients for specific API endpoints.
My first app, [Squeezefox](https://github.com/freddyb/squeezefox) is a remote control for Logitech Squeezebox Wifi Radios.
The other one, [wallabag-fxos](https://github.com/freddyb/wallabag-fxos) is a Firefox OS client for the *[Pocket](https://getpocket.com/) clone* [Wallabag](https://wallabag.org/).

The only feature that makes both of these apps so Firefox OS specific is their use of `systemXHR`: In Firefox OS, an [XMLHttpRequest (XHR)](https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest) instantiated with the `{mozSystem: true}` parameter is allowed to issue HTTP requests towards all origins. This is what allows my apps to be configured to talk with the user's wallabag instance (or squeezebox device).

I myself do not use those apps very heavily myself anymore and don't think I would make a great maintainer. But I do strongly believe in webapps and the future of the web regardless of the success of particular platforms, and I want these apps to be useful - regardless of the user agent.

For this reason, I suggest re-architecting applications who rely on it to be freed from proprietary technologies like `systemXHR`: The idea is to suggest users they self-host these apps on the same origin where they already host their main endpoint. Both wallabag and squeezebox servers (aka logitech media servers) allow hosting additional static files besides those which are built-in.
By removing some app-specific endpoint settings and defaulting to request against `location.href`, those apps can become more universally usable in its current form without any extra permissions or vendor-specific extensions.

Users who want to keep my apps in their Firefox OS/B2G OS specific nature, may keep using them as is. I have saved their current state in branches called `fxos-legacy`.

 * [https://github.com/wallabag/wallabag-fxos/tree/fxos-legacy](https://github.com/wallabag/wallabag-fxos/tree/fxos-legacy)
 * [https://github.com/freddyb/squeezefox/tree/fxos-legacy](https://github.com/freddyb/squeezefox/tree/fxos-legacy)
 
I will continue to welcome contributions to both the new architecture as well as the legacy branches, but I strongly recommend forking my projects if folks intend to use them productively in the future. But starting now, I will not commit to actively drive the development of either.
