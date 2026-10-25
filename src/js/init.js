/* ================= start the tools ================= */
$$(".widget[data-tool]").forEach(function (el) {
  var f = TOOLS[el.getAttribute("data-tool")];
  if (!f) { el.innerHTML = '<p class="werr" style="padding:12px 16px">Unknown tool "' + esc(el.getAttribute("data-tool")) + '".</p>'; return; }
  try { f(el); }
  catch (e) { el.innerHTML = '<p class="werr" style="padding:12px 16px">This tool could not start: ' + esc(e.message) + "</p>"; if (window.console) console.error(e); }
});
refresh();
