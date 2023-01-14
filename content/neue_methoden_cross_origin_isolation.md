Title: Neue Methoden für Cross-Origin Isolation: Resource, Opener & Embedding Policies mit COOP, COEP, CORP und CORB
Date: 2022-11-10
Author: Frederik
Slug: neue_methoden_cross_origin_isolation
tags: websecguide


*This document sat in my archives.
I originally created this so I have notes for my
participation in the Working Draft podcast - a German podcast
for web developers. That's why this article is in German as well.
The [podcast episode 452](https://workingdraft.de/452/) was published in 2020,
but I never published this document.
In the interest of breathing some live into this blog, here it is. Have fun!*

## Hintergrund: CORS & Same-Origin Policy

Die erste und wichtigste Grundregel in Sachen Web- & Browser-Sicherheit
ist die Same-Origin Policy. Sie bestimmt, dass alle Webseiten im
gleichen *Origin* auch mit den gleichen Rechten ausgestattet sind. Ein
Origin ist das Tripel von "Scheme, Host, Port".

Das bedeutet insbesondere, dass JavaScript keinen Zugriff auf Inhalte
aus anderen Origins erhält.

Wenn man also ein Bild, iframe oder Popup von einem anderen Origin lädt,
dann kann man es zwar **darstellen** lassen, aber eben **nicht per
JavaScript auslesen.** Egal ob via canvas, `iframe.contentDocument`,
`popup.contentDocument` usw.

Wichtig ist noch zu erwähnen, dass hier etwas namens "ambient authority"
greift: Wenn ein iframe von, sagen wir mal twitter.com (z.B. ein
Tweet-Knopf) angezeigt wird, schickt der Browser die Cookies für
twitter.com mit, so dass Twitter die Antwort auf den aktuellen Account
des aktuellen Benutzers anpassen kann.

Eine Ausnahme bietet hier CORS, das Cross-Origin Resource Sharing. Eine
Seite kann explizit erlauben, von anderen Origins gelesen zu werden,
wenn sie in dem Response Header eine entsprechende Erlaubnis per CORS.
Der häufigste header im Response lautet

`Access-Control-Allow-Origin: *`, damit sind alle Webseiten erlaubt, die
Datei zu laden UND auszulesen.

Wenn man möchte, kann man hier noch zwischen anonymen und credentialed
requests unterscheiden:

Mit dem `*` im ACAO-Header wird jedem das Lesen erlaubt. Das besondere am
`*` ist, dass implizit nur anonyme Requests erlaubt werden.

## Probleme die Same-Origin Policy und CORS nicht lösen

Die Same-Origin Policy ist eine mächtige, allgegenwärtige Maßnahme,
lässt jedoch einige Probleme ungelöst.

### XSLeaks

Der Angriff des sogenannten Cross-Site Leaks besteht schon seit gut 10
Jahren, ist aber kürzlich erneut in den Fokus gerückt. Ein
xsleak-Angriff macht sich bestimmtes Browserverhalten (zum Beispiel)
Timing zu nutze um Informationen über eine cross-origin Webseite zu
erhalten. Ein ganz einfaches Beispiel ist eine Seite, die *nur nach dem
Login* einen `<iframe>` anzeigt. Wenn ein Angreifer nun diese Seite
selbst in ein `<iframe>` öffnet, kann der Angreifer über
iframeEl.contentWindow.length herausfinden, ob die Seite weitere frames
beinhält und somit deduzieren ob der Benutzer eingeloggt ist.

Natürlich wissen wir alle, dass es eine schlechte Idee ist, dem
Angreifer zu erlauben unsere Seite in einem `<iframe>` zu öffnen,
deswegen gibt es ja die CSP frame-ancestors direktive & X-Frame-Options.

Derselbe Angriff funktioniert nur leider ebenfalls mit einem Popup bzw
der Referenz, die aus window.open fällt. Ferner lässt sich eben diese
Schwachstelle nicht aufheben, da Browser hier die
Rückwärtskompatibilität für existierende Webseiten wahren müssen.

Unter dem Begriff XSLeaks gibt es allerdings noch viele weitere
Techniken:

-   history.length lässt sich benutzen um redirects zu erkennen
    (nützlich für Login detection in login_and_then-Patterns in
    Webseiten)

-   Bilder, Videos, Audio erlauben das ausmessen von metadaten
    (A/V-Länge, Bilddimensionen)

-   Request timing (wie lange dauert ein fetch())

-   Leak of HTTP request done by exhausting the Network pool

### Spectre

Anfang 2018 veröffentlichte eine Gruppe von Sicherheitsforschern die
Sicherheitslücken Spectre & Meltdown. Diese Schwachstellen betreffen die
gängigsten CPUs von u.a. AMD, Intel. Durch cleveres Ausnutzen einer
Optimierung (speculative branching), die so vom Angreifer kontrolliert
wird, dass sie nicht greift und eine "branch misprediction" rückgängig
gemacht werden soll, ist es dem Angreifer möglich den gesamten Speicher
innerhalb des selben laufenden Prozesses auszulesen. Ferner hat ein Team
von Microsoft Vulnerability Research gezeigt, dass sich diese Lücke via
JavaScript ausnutzen lässt.

Spectre ist insbesondere für Browser ein Problem, da sich mehrere
Origins normalerweise einen Prozess teilen.

Diese Angriffe benötigen meist APIs für Shared Memory, wie
SharedArrayBuffer. Daher haben sich die Browser darauf geeinigt
SharedArrayBuffer vorübergehend abzuschalten.

### Zusammenfassend: Sicherheitslücken vermeiden, Zugriff zu SharedArrayBuffer wieder erlangen:

Es gibt sinnige Bestrebungen, sich weiter von anderen Webseiten
fernzuhalten, als nur durch die Same-Origin Policy forciert.

Informationen zu Fenstern aus anderen Origins können nicht vollständig
aus dem jeweiligen Prozess rausgehalten werden, zum Beispiel durch `<img
src>`.

Im Zuge dessen, sind Browser dazu übergegangen jedem Origin seinem
eigenen Prozess zuzuweisen. Das nennen wir Site-Isolation bzw. bei
Firefox "Project Fission".

Normalerweise würde der Browser ungefähr jedem Tab einen eigenen Prozess
zuweisen. Mit "Site Isolation" benötigen wir für jeden iframe einen
weiteren Prozess. Für eine News-Webseite wie cnn.com werden statt einem
Prozess nun auf einmal etwa 14 Prozesse benötigt.

# Neue Methoden für Cross-Origin Isolation

Aufgrund der neuen Angriffe und der neuen Browser-Architektur, ziehen es
bestimmte Webseiten nun vor sich und ihr Origin komplett zu isolieren.
Wenn man als Webseite in seinem komplett eigenen Tab ist - ohne
Ausnahme, dann wäre auch ein Spectre-Angriff nicht mehr problematisch.
Alles was ausgelesen werden kann, ist ohnehin eigene Information. Um das
zu ermöglichen, wurden ein paar neue Sicherheitsmechanismen in Form
eines HTTP Response Headers eingeführt. Eine Kombination derer erlaubt
es, als "crossOriginIsolated" zu gelten und somit wieder Zugriff auf
SharedArrayBuffer zu erhalten.

Hier nun ein kurzer Überblick über die neuen Cross-Origin primitiven:

## Cross-Origin-Opener-Policy (COOP)

`Cross-Origin-Opener-Policy: unsafe-none | same-origin-allow-popups | same-origin`

Unter Zuhilfenahme von Cross-Origin-Opener-Policy, kann eine Seite
explizit sagen, dass es keine window-handles (opener, popup) für Fenster
aus anderen Origins geben darf:

Hierfür senden wir `Cross-Origin-Opener-Policy: same-origin`.

## Cross-Origin-Embedder-Policy (COEP)

`Cross-Origin-Embedder-Policy: unsafe-none | require-corp | credentialless`

Wenn man COOP einsetzt besteht immer noch die Möglichkeit, dass man
selbst noch irgendwelche Cross-Origin Resourcen nachlädt (versehentlich,
redirects, usw.). Mit `Cross-Origin-Embedder-Policy: require-corp`
kann man sicher stellen, dass das Dokument nur Ressourcen in den Prozess
lädt, die von dem eigenen Origin sind oder es explizit erlaubt (durch
CORP. siehe unten) .

Wenn der Wert `credentialless` gesetzt ist, werden cross-origin Inhalte
ohne Cookies (credentials) angefordert. Das erlaubt Interaktionen mit
Webseiten, die nicht explizit "CORP" benutzen.

## COOP + COEP = `crossOriginIsolated`

Nur wenn man COOP+COEP einsetzt, erhält eine Website das Attribut
`window.crossOriginIsolated` als true. Nur, wenn man sich mit seinen
eigenen (plus eventuell öffentlichen) Daten in einem eigenen Prozess
abschottet, erhält man Zugriff auf `SharedArrayBuffer` und einen besonders
genauen Timer in der Performance API.

## CORP

`Cross-Origin-Resource-Policy: same-site | same-origin | cross-origin`

Mit CORP kann man, in etwa analog zu CORS, eine Ressource freischalten
und für den Gebrauch als öffentlich jenseits der Prozessgrenzen hinweg
deklarieren

## CORB bzw. ORB

Im Gegensatz zu den letzt genannten Methoden sind CORB, ORB **kein**
HTTP Header, sondern eine Festlegung, wie ein Browser gewisse Ressourcen
zu laden hat:. Die Idee basiert darauf, dass cross-origin Resourcen mit
"zweifelhaften Content-Typen" so blockiert werden, dass sie für den
Webprozess als "Network Error" dargestellt werden. Weitestgehend, geht
es darum Inhalte bereits an der Prozessgrenze zu blockieren, wenn nicht
eindeutig klar ist, dass sie für den Gebrauch wirklich erlaubt sind.
Typische Beispiele sind Inhalte mit Content-Type `text/plain`, welches
dann über `<script>` geladen werden könnten und trotz Syntaxfehler im
Prozessspeicher landen. Dies wird künftig nicht mehr möglich sein.

## Ausblick

Da die Themen xsleaks und auch Spectre noch relativ jung sind, ist zu
erwarten dass es weitere Mechanismen, Einschränkungen oder neue Werte
für die hier vorgestellten Response Header entwickelt werden. Bereits
jetzt werden Mechanismen wie
"[restrict-properties](https://github.com/hemeryar/explainers/blob/main/coop_restrict_properties.md)"
für Cross-Origin-Opener Policy vorgeschlagen, was die Isolation
beibehalten soll aber OAuth-Flows über pop ups ermöglichen könnte.

Es wird sich zeigen, was hier ausreichend ist und bleibt.
