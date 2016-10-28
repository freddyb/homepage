Title: Revoke App Permissions on Firefox OS
Date: 2014-08-24
Slug: revoking-permissions-on-firefox-os
Author: Frederik

On Firefox OS (FxOS), every app has its own set of permissions. The operating system makes sure that an app may only do things that are requested in the [app manifest](https://developer.mozilla.org/en-US/Apps/Build/Manifest).
Some of these permissions are always set to *Ask*. Sometimes just because the web platform is built this way. A common example is the geolocation permission:

<center>
![geolocation prompt](/images/geolocation-prompt.png)
</center>

There's also the [Alarms API](https://developer.mozilla.org/en-US/docs/Web/API/Alarm_API), for example. It allows applications to get opened at a specific time. There is nothing inherently bad with precise alarm functions that honor timezones (or not). But it is hard to know what the App will do with it. This gets exceedingly difficult to explain to users, especially when it comes to technical terms and features like the `tcp-socket` permission.

The security model of Firefox OS is based on contextual prompts. So for APIs that are understandable and human meaningful like geolocation, using the camera or recording audio the OS will prompt the user. You can save & remember these choices and later revisit them in the Settings app under "App Permissions". You may set them to *Allow*, *Prompt*, or *Deny*.

For simplicity's sake, all permissions default to something that the inventor's of these APIs deemed safe. For `tcp-sockets` and `alarms` this is *Allow*. For geolocation it's *Prompt*.
If you want to know more about the default permission settings, the [App Manager](https://developer.mozilla.org/en-US/Firefox_OS/Using_the_App_Manager#Device_panel_2) can show you how the table looks like for your phone. Here's an excerpt generated on my Flame device on FxOS 2.0:

<a href="/images/permission-table-2.0.png" title="click for a full list">
![permissions table](/images/permission-table-cut.png)
</a>

But what if you *are* tech savvy? What if you *do* want to revoke or be asked for permissions that are a bit hard to explain? 

To bridge this gap and empower tech savvy & paranoid privacy enthusiasts, [I have created](https://bugzilla.mozilla.org/show_bug.cgi?id=1049371) a developer settings that shows a verbose app permissions list. It enhances the normal App Permissions panel of the Settings app.

Starting with Firefox 2.1, you may activate the [developer settings](https://developer.mozilla.org/en-US/Firefox_OS/Debugging/Developer_settings) and tick the checkbox near "Verbose App Permissions". The typical list in the Settings app will then show you all the permissions an app has and allows you to set them to *Allow*, *Prompt* or *Deny*. This feature, however, only targets the Privileged apps. These are apps that come through the Marketplace. For now, we can not revoke permissions for the built-in apps (the permission `set()` call throws).


Beware that you may break the app that you wish to contain - just because it is not designed to cope with failure. Some APIs are designed with an asynchronous request/response pattern. These will likely work fine and not throw an unrecoverable exception. But it still means that the developer has had to set an error handler, or the app might be indefinitely stuck in a waiting state.
