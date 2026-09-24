// Injected into the pygbag build by build_web.sh.
// The Python game talks to the page through these hooks: saves, online play and chat.
(function () {
  "use strict";
  var KEY = "aswc_save";
  var queue = [];          // messages waiting for the game to poll
  var netUp = false;

  // Fill the window. pygbag centres a fixed-size canvas; this scales it up to the
  // biggest 16:9 rectangle the window holds, with the pixels kept crisp.
  function fillWindow() {
    try {
      var css = document.createElement("style");
      css.id = "aswc-fill";
      css.textContent =
        "html,body{margin:0;padding:0;height:100%;overflow:hidden;background:#000}" +
        "canvas{position:absolute!important;top:50%!important;left:50%!important;" +
        "transform:translate(-50%,-50%)!important;" +
        "width:min(100vw, calc(100vh * 16 / 9))!important;" +
        "height:min(100vh, calc(100vw * 9 / 16))!important;" +
        "max-width:none!important;max-height:none!important;" +
        "image-rendering:pixelated;image-rendering:crisp-edges;display:block!important}";
      (document.head || document.documentElement).appendChild(css);
    } catch (e) { /* the game still runs, just letterboxed */ }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fillWindow);
  } else {
    fillWindow();
  }

  function up(msg) {
    try { parent.postMessage(msg, location.origin); } catch (e) { /* not framed */ }
  }

  // ---- saves
  window.aswcSave = function (text) {
    try { localStorage.setItem(KEY, String(text)); } catch (e) { /* private mode */ }
    up({ type: "aswc-save", save: String(text) });
  };

  // ---- online play: the page owns the connection, the game just posts and polls
  window.aswcNetSend = function (json) {
    up({ type: "aswc-net", msg: String(json) });
  };
  window.aswcNetPoll = function () {
    if (!queue.length) return "";
    var out = JSON.stringify(queue);
    queue = [];
    return out;
  };
  window.aswcNetUp = function () { return netUp; };

  // ---- chat
  window.aswcChatSend = function (text) {
    up({ type: "aswc-chat", text: String(text) });
  };

  // ---- match result (online): the page records it on the ladder
  window.aswcMatchResult = function (json) {
    up({ type: "aswc-result", result: String(json) });
  };

  window.addEventListener("message", function (e) {
    if (e.origin !== location.origin || !e.data) return;
    var d = e.data;
    if (d.type === "aswc-load" && typeof d.save === "string") {
      try { localStorage.setItem(KEY, d.save); } catch (err) { /* ignore */ }
    } else if (d.type === "aswc-net" && d.msg) {
      try { queue.push(JSON.parse(d.msg)); } catch (err) { /* ignore */ }
      if (queue.length > 120) queue.splice(0, queue.length - 120);
    } else if (d.type === "aswc-netstate") {
      netUp = !!d.up;
    }
  });

  up({ type: "aswc-ready" });
})();
