// Injected into the pygbag build by build_web.sh.
// The Python game talks to the page through these hooks: saves, online play and chat.
(function () {
  "use strict";
  var KEY = "aswc_save";
  var queue = [];          // messages waiting for the game to poll
  var netUp = false;

  // ---- fill the window
  // pygbag draws into a fixed-size canvas and leaves it sitting in the middle of the page.
  // This scales it to the biggest rectangle of the same shape the window holds, and forces
  // every wrapper around it out of the way. It re-applies on resize and on a timer, because
  // the runtime sets its own inline styles on the canvas whenever the display mode changes.
  function clearFor(el) {
    el.style.setProperty("position", "fixed", "important");
    el.style.setProperty("left", "0", "important");
    el.style.setProperty("top", "0", "important");
    el.style.setProperty("width", "100%", "important");
    el.style.setProperty("height", "100%", "important");
    el.style.setProperty("max-width", "none", "important");
    el.style.setProperty("max-height", "none", "important");
    el.style.setProperty("margin", "0", "important");
    el.style.setProperty("padding", "0", "important");
    el.style.setProperty("overflow", "visible", "important");
    el.style.setProperty("transform", "none", "important");
    el.style.setProperty("background", "#000", "important");
  }

  function fit() {
    var c = document.querySelector("canvas");
    if (!c) return;
    for (var el = c.parentElement; el && el !== document.documentElement; el = el.parentElement) {
      if (el.tagName === "BODY") {
        el.style.setProperty("margin", "0", "important");
        el.style.setProperty("padding", "0", "important");
        el.style.setProperty("overflow", "hidden", "important");
        el.style.setProperty("background", "#000", "important");
      } else {
        clearFor(el);
      }
    }
    var w = window.innerWidth || document.documentElement.clientWidth;
    var h = window.innerHeight || document.documentElement.clientHeight;
    var cw = c.width || 16, ch = c.height || 9;
    var k = Math.min(w / cw, h / ch);                 // keep the shape, fill what we can
    var fw = Math.max(1, Math.round(cw * k));
    var fh = Math.max(1, Math.round(ch * k));
    c.style.setProperty("position", "fixed", "important");
    c.style.setProperty("left", Math.round((w - fw) / 2) + "px", "important");
    c.style.setProperty("top", Math.round((h - fh) / 2) + "px", "important");
    c.style.setProperty("right", "auto", "important");
    c.style.setProperty("bottom", "auto", "important");
    c.style.setProperty("width", fw + "px", "important");
    c.style.setProperty("height", fh + "px", "important");
    c.style.setProperty("max-width", "none", "important");
    c.style.setProperty("max-height", "none", "important");
    c.style.setProperty("margin", "0", "important");
    c.style.setProperty("transform", "none", "important");
    c.style.setProperty("image-rendering", "pixelated", "important");
    c.style.setProperty("display", "block", "important");
    c.style.setProperty("touch-action", "none", "important");
  }

  function startFitting() {
    fit();
    addEventListener("resize", fit);
    addEventListener("orientationchange", fit);
    var n = 0;
    var timer = setInterval(function () {
      fit();
      if (++n > 120) {                                 // after a minute the layout has settled
        clearInterval(timer);
        setInterval(fit, 2000);
      }
    }, 500);
    try {
      var css = document.createElement("style");
      css.textContent = "html,body{margin:0;padding:0;height:100%;overflow:hidden;background:#000}";
      (document.head || document.documentElement).appendChild(css);
    } catch (e) { /* the inline styles above already did the work */ }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startFitting);
  } else {
    startFitting();
  }
  addEventListener("load", fit);

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
