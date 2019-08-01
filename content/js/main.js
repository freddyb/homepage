// Unhiding email addreseses.
// Mostly obscurity, but hopefully limiting spam.
window.addEventListener("load", function() {
  var nodelist = document.querySelectorAll(".emailaddr");
  for (var n = 0; n < nodelist.length; n++) {
    var node = nodelist[n];
    var r = node.dataset.crypt;
    var e = "";
    for (i = 0; i < r.length; i++) {
      e += String.fromCharCode(r.charCodeAt(i) ^ 0x07);
    }
    node.innerHTML = "<a href='mailto:" + e + "'>" + e + "</a>";
  }
});
// load bigger styles later
// (so pygment don't block page load)
var loadStyles = function() {
  var lcode = document.createElement("link");
  lcode.rel = "stylesheet";
  lcode.href = "/theme/css/pygment.css"; // code highlighting
  var h = document.getElementsByTagName("head")[0];
  h.parentNode.insertBefore(lcode, h);
};
var raf =
  requestAnimationFrame ||
  mozRequestAnimationFrame ||
  webkitRequestAnimationFrame ||
  msRequestAnimationFrame;
if (raf) raf(loadStyles);
else window.addEventListener("load", loadStyles);
