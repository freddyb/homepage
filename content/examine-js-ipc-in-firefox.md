title: Examine Firefox Inter-Process Communication using JavaScript in 2023
Author: Frederik Braun
Date: 2023-04-17

*This is my update to the 2021 JavaScript IPC [blog post](https://blog.mozilla.org/attack-and-defense/2021/04/27/examining-javascript-inter-process-communication-in-firefox/) from the Firefox Attack & Defense blog.*

Firefox uses Inter-Process Communication (IPC) to implement privilege separation, which makes it an important cornerstone in our security architecture. A previous blog post focused on <a href="https://blog.mozilla.org/attack-and-defense/2021/01/27/effectively-fuzzing-the-ipc-layer-in-firefox/">fuzzing the C++ side of IPC</a>. This blog post will look at IPC in JavaScript, which is used in various parts of the user interface. First, we will briefly revisit the multi-process architecture and upcoming changes for <a href="https://wiki.mozilla.org/Project_Fission">Project Fission</a>, Firefox’ implementation for Site Isolation. We will then move on to examine two different JavaScript patterns for IPC and explain how to invoke them. Using Firefox’s Developer Tools (DevTools), we will be able to debug the browser itself.

Once equipped with this knowledge, we will revisit a sandbox escape bug that was used in a<a href="https://blog.coinbase.com/responding-to-firefox-0-days-in-the-wild-d9c85a57f15b"> 0day attack against Coinbase in 2019</a> and reported as <a href="https://www.mozilla.org/en-US/security/advisories/mfsa2019-19/#CVE-2019-11708">CVE-2019-11708</a>. This 0day-bug has found extensive coverage in<a href="https://blog.exodusintel.com/2020/11/10/firefox-vulnerability-research-part-2/"> blog posts</a> and <a href="https://github.com/0vercl0k/CVE-2019-11708">publicly available exploits</a>. We believe the bug provides a great case study and the underlying techniques will help identify similar issues. Eventually, by finding more sandbox escapes you can help secure hundreds of millions of Firefox users as part of the <a href="https://www.mozilla.org/en-US/security/client-bug-bounty/">Firefox Bug Bounty Program</a>.
<h2><b>Multi-Process Architecture Now and Then</b></h2>
As of April 2021, Firefox uses one privileged process to launch other process types and coordinate activities. These types are web content processes, semi-privileged web content processes (for special websites like accounts.firefox.com or addons.mozilla.org) and four kinds of utility processes for web extensions, GPU operations, networking or media decoding. Here, we will focus on the communication between the main process (also called "parent") and a multitude of web processes (or "content" processes).

Firefox is shifting towards a new security architecture to achieve Site Isolation, which moves from a “process per tab” to a “process per <a href="https://html.spec.whatwg.org/multipage/origin.html#sites">site</a>” architecture.

The parent process acts as a broker and trusted user interface host. Some features, like our settings page at about:preferences are essentially web pages (using HTML and JavaScript) that are hosted in the parent process. Additionally, various control features like modal dialogs, form auto-fill or native user interface pieces (e.g., the <code>&lt;select&gt;</code> element) are also implemented in the parent process. This level of privilege separation also requires receiving messages from content processes.

Let's look at JSActors and MessageManager, the two most common patterns for using inter-process communication (IPC) from JavaScript:
<h3><b>JSActors</b></h3>
Using a <a href="https://firefox-source-docs.mozilla.org/dom/ipc/jsactors.html">JSActor</a> is the preferred method for JS code to communicate between processes. JSActors always come in pairs - with one implementation living in the child process and the counterpart in the parent. There is a separate parent instance for every pair in order to closely and consistently associate a message with either a specific content window (JSWindowActors), or child process (JSProcessActors).

Since all JSActors are lazy-loaded we suggest to exercise the implemented functionality at least once, to ensure they are all present and allow for a smooth test and debug experience.

<img class="size-full wp-image-229" src="http://blog.mozilla.org/attack-and-defense/files/2021/04/jsactors.png" alt="Inter-Process Communication building on top of JSActors and implemented as FooParent and FooChild" width="555" height="533" />


The example diagram above shows a pair of JSActors called <i>FooParent</i> and <i>FooChild</i>. Messages sent by invoking <i>FooChild</i> will only be received by a <i>FooParent</i>. The child instance can send a <i>one-off</i> message with <code>sendAsyncMesage("someMessage", value)</code>. If it needs a response (wrapped in a <code>Promise</code>), it can send a query with <code>sendQuery("someMessage", value)</code>.

The parent instance must implement a <code>receiveMessage(msg)</code> function to handle all incoming messages. Note that the messages are namespace-tied between a specific actor, so a <i>FooChild</i> could send a message called <i>Bar:DoThing</i> but will never be able to reach a <i>BarParent</i>. Here is some example code (<a href="https://searchfox.org/mozilla-central/diff/3075dbd453f011aaf378bcac6b2700dccfcf814c/browser/actors/PromptParent.jsm">permalink, revision from March 25th</a>) which illustrates how a message is handled in the parent process.

<img class="size-full wp-image-221" src="http://blog.mozilla.org/attack-and-defense/files/2021/03/promptparent-excerpt.png" alt="Code sample for a receiveMessage function in a JSActor" width="506" height="275" />

As illustrated, the <i>PromptParent</i> has a <code>receiveMessage</code> handler (line 127) and is passing the message data to additional functions that will decide where and how to open a prompt from the parent process. Message handlers like this and its callees are a source of untrusted data flowing into the parent process and provide logical entry points for in-depth audits
<h3><b>Message Managers</b></h3>
Prior to the architecture change in Project Fission, most parent-child IPC occurred through the MessageManagers system. There were multiple message managers, including the per-process message manager and the content frame message manager, which was loaded per-tab.

Under this system, JS in both processes would register message listeners using the <code>addMessageListener</code> methods and would send messages with <code>sendAsyncMessage</code>, that have a name and the actual content. To help track messages throughout the code-base their names are usually prefixed with the components they are used in (e.g., <code>SessionStore:restoreHistoryComplete</code>).

Unlike JSActors, Message Managers need verbose initialization with addMessageListener and are not tied together. This means that messages are available for all classes that listen on the same message name and can be spread out through the code base.

<img class="wp-image-230 size-full" src="http://blog.mozilla.org/attack-and-defense/files/2021/04/image6.png" alt="Inter-Process Communication using MessageManager" width="555" height="533" /> Inter-Process Communication using MessageManager

As of late April 2021, our AddonsManager - the code that handles the installation of WebExtensions into Firefox - is using MessageManager APIs:

<img class="size-full wp-image-222" src="http://blog.mozilla.org/attack-and-defense/files/2021/03/addonsmanager-receivemessage-code-sample.png" alt="Code sample for a receiveMessage function using the MessageManger API" width="511" height="261" /> Code sample for a <code>receiveMessage</code> function using the MessageManger API

The code (<a href="https://searchfox.org/mozilla-central/rev/6309f663e7396e957138704f7ae7254c92f52f43/toolkit/mozapps/extensions/addonManager.js#216">permalink to exact revision</a>) for setting a MessageManager looks very similar to the setup of a JSActor with the difference that messaging can be used synchronously, as indicated by the <a href="https://searchfox.org/mozilla-central/rev/6309f663e7396e957138704f7ae7254c92f52f43/toolkit/mozapps/extensions/amInstallTrigger.jsm#64">sendSyncMessage call in the child process</a>. Except for the lack of lazy-loading, you can assume the same security considerations: Just like with JSActors above, the <code>receiveMessage</code> function is where the untrusted information flows from the child into the parent process and should therefore be the focus of additional scrutiny.

Finally, if you want to inspect <code>MessageManager</code> traffic live, you can use our <a href="https://developer.mozilla.org/en-US/docs/Mozilla/Developer_guide/Gecko_Logging">logging framework</a> and run Firefox with the environment variable <code>MOZ_LOG</code> set to <code>MessageManager:5</code>. This will log the received messages for all processes to the shell and give you a better understanding of what’s being sent and when.
<h2><b>Inspecting, Debugging, and Simulating JavaScript IPC</b></h2>
Naturally, source auditing a <code>receiveMessage</code> handler is best paired with testing. So let's discuss how we invoke these functions in the child process and attach a JavaScript debugger to the parent process. This allows us to simulate a scenario where we have already full control over the child process. For this, we recommend you download and test against <a href="https://nightly.mozilla.org/">Firefox Nightly</a> to ensure you're testing the latest code - it will also give you the benefit of being in sync with codesearch for the latest revisions at <a href="https://searchfox.org">https://searchfox.org</a>. For best experience, we recommend you <a href="https://nightly.mozilla.org/">download Firefox Nightly</a> right now and follow this part of the blog post step by step.

<b>DevTools Setup - Parent Process</b>

First, set up your Firefox Nightly to enable browser debugging. Note that the instructions for how to enable browser debugging can change over time, so it's best you cross-check with the<a href="https://developer.mozilla.org/en-US/docs/Tools#debugging_the_browser"> instructions for Debugging the browser on MDN</a>.

Open the Developer Tools, click the "<b>···</b>" button in the top-right and find the settings. Within <i>Advanced settings</i> in the bottom-right, check the following:
<ul>
  <li aria-level="1"><i>Enable browser chrome and add-on debugging toolboxes</i></li>
  <li aria-level="1"><i>Enable remote debugging</i></li>
</ul>

Restart Firefox Nightly and open the Browser debugger (Tools -&gt; Browser Tools -&gt; Browser Toolbox). This will open a new window that looks very similar to the common DevTools.

This is your debugger for the parent process (i.e., Browser Toolbox = Parent Toolbox).

The frame selector button, which is left of the three balls "<b>···</b>" will allow you to select between windows. Select browser.xhtml, which is the main browser window. Switching to the Debug pane will let you search files and find the Parent actor you want to debug, as long as they have been already loaded. To ensure the <em>PromptParent</em> actor has been properly initialized, open a new tab on e.g. <a href="https://example.com">https://example.com</a> and make it call <code>alert(1)</code> from the normal DevTools console.

[caption id="attachment_223" align="aligncenter" width="1847"]<img class="size-full wp-image-223" src="http://blog.mozilla.org/attack-and-defense/files/2021/03/alert-as-triggered-from-website-in-parent-devtools.png" alt="Hitting a breakpoint in Firefox’s parent process using Firefox Developer Tools (left)" width="1847" height="1173" /> Hitting a breakpoint in Firefox’s parent process using Firefox Developer Tools [left](/caption)

You should now be able to find PromptParent.jsm (Ctrl+P) and set a debugger breakpoint for all future invocations (see screenshot above). This will allow you to inspect and copy the typical arguments passed to the Prompt JSActor in the parent.

Note: Once you hit a breakpoint, you can enter code into the Developer Console which is then executed within the currently intercepted function.

<b>DevTools Setup - Child Process</b>

Now that we know how to inspect and obtain the parameters which the parent process is expecting for <code>Prompt:Open</code>, let's try and trigger it from a debugged child process: Ensure you are on a typical web page, like <a href="https://example.com">https://example.com</a>, so you get the right kind of content child process. Then, through the Tools menu, find the "Browser Content Toolbox". Content here refers to the child process (Content Toolbox = Child Toolbox).

Since every content process might have many windows of the same site associated with it, we need to find the current window. This snippet assumes it is the first tab and gets the Prompt actor for that tab:

<code>actor = tabs[0].content.windowGlobalChild.getActor("Prompt");</code>

Now that we have the actor, we can use the data gathered in the parent process and send the very same data. Or maybe, a variation thereof:

<code>actor.sendQuery("Prompt:Open", {promptType: "alert", title: "👻", modalType: 1, promptPrincipal: null, inPermutUnload: false, _remoteID: "id-lol"});</code>

<img class="size-full wp-image-225" src="http://blog.mozilla.org/attack-and-defense/files/2021/03/Bildschirmfoto-vom-2021-03-26-15-45-18.png" alt="Invoking JavaScript IPC from Firefox Developer Tools (bottom right) and observing the effects (top right)" width="1848" height="1169" /> Invoking JavaScript IPC from Firefox Developer Tools (bottom right) and observing the effects (top right)

In this case, we got away with not sending a reasonable value for <code>promptPrincipal</code> at all. This is certainly not going to be true for all message handlers. For the sake of this blog post, we can just assume that a <em>Principal</em> is the implementation of an <a href="https://html.spec.whatwg.org/multipage/origin.html#concept-origin">Origin</a> (and for background reading, we recommend an explanation of the <em>Principal</em> Objects in our two-series blog post "Understanding Web Security Checks in Firefox": See <a href="https://blog.mozilla.org/attack-and-defense/2020/06/10/understanding-web-security-checks-in-firefox-part-1/">part 1</a> and <a href="https://blog.mozilla.org/attack-and-defense/2020/08/05/understanding-web-security-checks-in-firefox-part-2/">part 2</a>).

In case you wonder why the content process is allowed to send a potentially arbitrary <em>Principal</em> (e.g., the origin): This is currently a known limitation and will be fixed while we are en route to full site-isolation (<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=1505832">bug 1505832</a>).

If you want to try to send another, faked origin - maybe from a different website or maybe the most privileged <em>Principal</em> - the one that is bypassing all security checks, the <em>SystemPrincipal</em>, you can use these snippets to replace the <em>promptPrincipal</em> in the IPC message:
<pre>const {Services} = ChromeUtils.import("resource://gre/modules/Services.jsm");
otherPrincipal = Services.scriptSecurityManager.createContentPrincipalFromOrigin("https://evil.test");
systemPrincipal = Services.scriptSecurityManager.getSystemPrincipal();</pre>
Note that validating the association between process and site is already <a href="https://searchfox.org/mozilla-central/rev/6309f663e7396e957138704f7ae7254c92f52f43/dom/ipc/ContentParent.cpp#1348">enforced in debug builds</a>. If you compiled your own Firefox, this will cause the content process to crash.
<h2><b>Revisiting Previous Security Issues</b></h2>
Now that we have the setup in place we can revisit the security vulnerability mentioned above: <a href="https://www.mozilla.org/en-US/security/advisories/mfsa2019-19/#CVE-2019-11708">CVE-2019-11708</a>.

The issue in itself was a typical logic bug: Instead of switching which prompt to open in the parent process, the vulnerable version of this code accepted the URL to an internal prompt page, implemented as an XHTML page. But by invoking this message, the attacker could cause the parent process to open any web-hosted page instead. This allowed them to re-open their content process exploit again in the parent process and escalate to a full compromise.

Let's take a look at  the diff for the security fix to see how we replaced the vulnerable logic and handled the prompt type switching in the parent process (<a href="https://searchfox.org/mozilla-central/diff/3075dbd453f011aaf378bcac6b2700dccfcf814c/browser/actors/PromptParent.jsm#141">permalink to source</a>).

<img class="size-full wp-image-226" src="http://blog.mozilla.org/attack-and-defense/files/2021/03/diff-prompt-coinbase-0day.png" alt="Handling of untrusted message.data before and after fixing CVE-2019-11708." width="629" height="419" /> Handling of untrusted <code>message.data</code> before and after fixing CVE-2019-11708.

You will notice that line 140+ used to accept and use a parameter named <code>uri</code>. This was fixed in a multitude of patches. In addition to only allowing certain dialogs to open in the parent process we also generally <a href="https://blog.mozilla.org/attack-and-defense/2020/07/07/hardening-firefox-against-injection-attacks-the-technical-details/">disallow opening web-URLs in the parent process</a>.

If you want to try this yourself, download a version of Firefox before 67.0.4 and try sending a <code>Prompt:Open</code> message with an arbitrary URL.
<h2><b>Next Steps</b></h2>
In this blog post, we have given an introduction to Firefox IPC using JavaScript and how to debug the child and the parent process using the Content Toolbox and the Browser Toolbox, respectively. Using this setup, you are now able to simulate a fully compromised child process, audit the message passing in source code and analyze the runtime behavior across multiple processes.

If you are already experienced with Fuzzing and want to analyze how high-level concepts from JavaScript get serialized and deserialized to pass the process boundary, please check our previous blog post on <a href="https://blog.mozilla.org/attack-and-defense/2021/01/27/effectively-fuzzing-the-ipc-layer-in-firefox/">Fuzzing the IPC layer of Firefox</a>.

If you are interested in testing and analyzing the source code at scale, you might also want to look into the <a href="https://blog.mozilla.org/attack-and-defense/2020/05/25/firefox-codeql-databases-available-for-download/">CodeQL databases</a> that we publish for all Firefox releases.

If you want to know more about how our developers port legacy MessageManager interfaces to JSActors, you can take another look at our <a href="https://firefox-source-docs.mozilla.org/dom/ipc/jsactors.html">JSActors documentation</a> and at how Mike Conley ported the popup blocker in his <a href="https://www.youtube.com/watch?v=mtIt6ir9GHU">Joy of Coding live stream Episode 204.</a>

Finally, we at Mozilla are really interested in the bugs you might find with these techniques - bugs like confused-deputy attacks, where the parent process can be tricked into using its privileges in a way the content process should not be able to (e.g. reading/writing arbitrary files on the filesystem) or UXSS-type attacks, as well as <a href="https://www.mozilla.org/en-US/security/client-bug-bounty/#exploit-mitigation-bounty">bypasses of exploit mitigations</a>. Note that as of April 2021, we are not enforcing full site-isolation. Bugs that allow one to impersonate another site will <i>not</i> yet be eligible for a bounty. Submit your findings through our <a href="https://www.mozilla.org/en-US/security/client-bug-bounty/#claiming-a-bounty">bug bounty program</a> and follow us at the<a href="https://twitter.com/attackndefense"> @attackndefense</a> Twitter account for more updates.
