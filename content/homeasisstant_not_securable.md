title: Home assistant can not be secured for internet access
date: 2024-12-15

### The Goal: Smart Heating Control

Home automation is a cool toy but also allows my house hold to be more energy efficient: My aim was to configure my home's heating to switch off when my family is away and turn back on when we return. This is achieved with home assistant, a popular open-source home automation platform, with location/presence notifications from mobile devices. To do this, the home assistant server needs to be accessible from the internet, as mobile devices must communicate with it remotely.

### The Constraints

One might suggest using a VPN to secure the connection. However, this approach is impractical for us for several reasons.
My main one being that not all devices in our family can connect to a VPN.
Given our family's constraints, I concluded that it's necessary to expose home assistant directly to the internet, which in turn introduces a security challenge: protecting the server from unauthorized access.

### The Security Dilemma

Home assistant allows authentication using username and password (and even two-factor authentication) as its primary security measure.
While this is a solid baseline, I don't think it's sufficient in case there are security issues in home assistant itself.
I want to provide defense in depth to protect against opportunistic attackers who regularly scan the internet for exposed systems.
This could be applied using a reverse HTTP(S) proxy. However, several limitations made this impossible:

- **Subdomains:** Home assistant could be hosted on a "secret" domain/subdomain, but I assume that DNS is not universally encrypted and leaks are to be expected.
- **No Basic Authentication Support:** Home assistant's mobile apps cannot handle URLs with embedded credentials (e.g., `https://user:pass@hostname`).
- **Path Limitations:** Home assistant must be hosted at the root path (`/`), preventing the use of an obscure web host path to deter scanners.
- **Authentication controls:** Home assistant responds to authentication failures without a HTTP 200 response that carries JSON data. This also makes it impossible to apply controls based on the amount of HTTP errors for too many authentication attempts.

These restrictions make it basically impossible to provide additional security mechanisms like web server authentication or hiding the service behind unconventional paths. As a result, home assistant's security depends solely on its internal measures.

### The Conclusion: A Disappointing State of Affairs

Despite its robust feature set, home assistant's architecture makes it challenging to secure against internet threats. Without the ability to implement defense-in-depth practices, I've concluded that home assistant is not properly securable for direct internet exposure. While it may adhere to software best practices internally, its design limitations prevent users from applying additional layers of protection elsewhere.

Home assistant's reliance on internal security mechanisms leaves much to be desired, especially for users who would like to apply additional access control. I believe this highlights the need for the home assistant community to address these concerns and improve its flexibility for advanced security configurations.
