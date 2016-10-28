Title: My thoughts on Tor appliances
Date: 2014-10-14
Slug: thoughts-on-tor-appliances
Author: Frederik


# Anonabox is not a magic bullet!

Yesterday, a lot of mainstream media (e.g., [WIRED](http://www.wired.com/2014/10/tiny-box-can-anonymize-everything-online/?mbid=social_twitter)) started reporting about [anonabox](https://www.kickstarter.com/projects/augustgermar/anonabox-a-tor-hardware-router), an "an open source embedded networking device designed specifically to run Tor.", to quote their Kickstarter campaign.

For those of you who don't know what Tor is: It's a network run by volunteers that anonymizes your internet traffic. With everyone in the network using someone else's address from time to time, it is becoming harder for an observer (e.g. the websites you browse) to find out who is who.

### Advertisements & Social Media kill Anonymity

This, of course only works until you go to a website like Facebook where you basically have to prove that you are you - because you have to login. But I don't want to talk about the behavioral constraints you have to consider when using Tor - their [official FAQ](https://www.torproject.org/docs/faq.html.en#WhatProtectionsDoesTorProvide) as well as many other documents have already addressed this.
What I want to talk about is Anonabox: I greatly support the idea of supporting the Tor network and adding as many nodes as possible. I agree that this is a great device to make this easier and hope that it will strengthen the Tor network in terms of bandwidth and diversity. I am quite sure that greater uptake will also help fixing some of the usability problems that come with browsing through Tor: A lot of websites block or discriminate against Tor users by disallowing them to register or post content - mostly because they are scared of abuse. Even though a non-anonymized stranger might possibly do as much damage as a Tor user. More Tor users is good! We also need Tor traffic which does recreational browsing (e.g., looking at animated gifs).

### What Anonabox can not do

OK, now that I have gotten this disclaimer out, here's what I *do* want to emphasize most: Anonabox[^1] is not going to change your browsing behavior. You have to remember that whenever you login with something, it is capable of tracking you along the web. This applies mostly to Social Networks which have wide-spread "share this" buttons (e.g., Twitter, Facebook), but may also apply to Advertising Networks as they also have a great visibility into the list of websites you visit, which gives them a lot of information about yourself.

But what's worse, is that **your browser is a highly functional, application platform** for running whatever code a websites offers you. This code is heavily restricted from accessing your machine[^2], but that still gives the website a great deal of control over your browsing context. And the context is enough to [generate a fingerprint](https://en.wikipedia.org/wiki/Canvas_fingerprinting) of your device that allows a marginally skilled techie to recognize you [whenever you come back](https://en.wikipedia.org/wiki/Evercookie).

Anonabox[^1] is incapable of modifying your browser or its functionality. It also can and should not look into your web traffic to prevent those bad things. Good internet traffic is encrypted traffic and when nobody should be able to look inside, this includes anonabox.
 
### Do not rely on a false sense of Anonymity

If you have to rely on being anonymous, you can not rely on anonabox alone. **If you care about anonymity, you must use a browser that has been patched and tamed towards privacy, not functionality**. Read the [Tor Warnings](https://www.torproject.org/download/download-easy.html.en#warning) and use the [Tor Browser](https://www.torproject.org/download/download-easy.html.en). This is the best way to stay anonymous with Tor.

 
 
 [^1]: This applies to all future and [previous](https://pogoplug.com/safeplug) incarnation of Tor appliances. But if you like to tinker (and safe some money), you could run the free [PORTAL](https://github.com/grugq/portal) software on that [Raspberry Pi](https://github.com/grugq/PORTALofPi) which is lying on your desk and waiting for a meaningful use case.

 [^2]: Well, a lot of browser exploits have proven this wrong. But let's not get into this for now.
