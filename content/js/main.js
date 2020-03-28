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
