// Injected into the pygbag build by build_web.sh.
// The Python game writes its save to localStorage and calls window.aswcSave(text);
// this hands it to the page, which puts it in the player's Firebase account.
(function () {
  "use strict";
  var KEY = "aswc_save";

  function up(msg) {
    try { parent.postMessage(msg, location.origin); } catch (e) { /* not framed */ }
  }

  window.aswcSave = function (text) {
    try { localStorage.setItem(KEY, String(text)); } catch (e) { /* private mode */ }
    up({ type: "aswc-save", save: String(text) });
  };

  window.addEventListener("message", function (e) {
    if (e.origin !== location.origin || !e.data) return;
    if (e.data.type === "aswc-load" && typeof e.data.save === "string") {
      try { localStorage.setItem(KEY, e.data.save); } catch (err) { /* ignore */ }
    }
  });

  up({ type: "aswc-ready" });
})();
