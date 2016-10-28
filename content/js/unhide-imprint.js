window.onload = function() {
        function unhide() {
                return atob("RnJlZGVyaWsgQnJhdW48YnI+Qm96ZW5lciBTdHIuIDIyPGJyPjEwODI1IEJlcmxpbg==");
        }
        function show() {
                o.innerHTML = unhide();
        }
        setTimeout(show, 3e4);
}
