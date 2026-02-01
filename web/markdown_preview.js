import { app } from "../../scripts/app.js";

const EXT_NAME = "ComfyUI.SimpleChat.MarkdownPreview";
const STYLE_ID = "simplechat-markdown-preview-style";

function chainCallback(object, property, callback) {
  if (!object) return;
  if (property in object && object[property]) {
    const callback_orig = object[property];
    object[property] = function () {
      const r = callback_orig.apply(this, arguments);
      return callback.apply(this, arguments) ?? r;
    };
  } else {
    object[property] = callback;
  }
}

function ensureStyles() {
  if (document.getElementById(STYLE_ID)) return;
  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.type = "text/css";
  style.innerHTML = `
  .simplechat-md-modal {
    position: fixed;
    right: 18px;
    top: 18px;
    width: min(720px, calc(100vw - 36px));
    height: min(70vh, 760px);
    background: var(--comfy-menu-bg);
    color: var(--fg-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    z-index: 9999;
    box-shadow: 0 16px 40px rgba(0,0,0,0.35);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .simplechat-md-modal header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 12px;
    border-bottom: 1px solid var(--border-color);
    background: rgba(0,0,0,0.08);
    font: 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  }
  .simplechat-md-modal header .title {
    opacity: 0.9;
  }
  .simplechat-md-modal header .actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .simplechat-md-modal header button {
    border: 1px solid var(--border-color);
    background: transparent;
    color: var(--fg-color);
    border-radius: 8px;
    padding: 4px 8px;
    cursor: pointer;
    font-size: 12px;
  }
  .simplechat-md-modal header button:hover {
    background: rgba(255,255,255,0.06);
  }
  .simplechat-md-body {
    padding: 12px;
    overflow: auto;
  }
  .simplechat-md-body pre, .simplechat-md-body code {
    background: rgba(0,0,0,0.16);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 8px 10px;
    overflow: auto;
  }
  .simplechat-md-body a {
    color: #ffd166;
  }
  .simplechat-md-body a:visited {
    color: #f4a261;
  }
  `;
  document.head.appendChild(style);
}

function loadScript(url) {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${url}"]`);
    if (existing) return resolve(true);
    const el = document.createElement("script");
    el.async = true;
    el.type = "text/javascript";
    el.src = url;
    el.addEventListener("load", () => resolve(true));
    el.addEventListener("error", () => reject(new Error(`Failed to load ${url}`)));
    document.body.appendChild(el);
  });
}

let _libsPromise = null;
async function ensureMarkdownLibs() {
  if (window.marked && window.DOMPurify) return;
  if (_libsPromise) return _libsPromise;
  const markedUrl = new URL("./vendor/marked.min.js", import.meta.url).href;
  const purifyUrl = new URL("./vendor/purify.min.js", import.meta.url).href;
  _libsPromise = (async () => {
    await loadScript(markedUrl);
    await loadScript(purifyUrl);
  })();
  return _libsPromise;
}

function escapeHtml(text) {
  return (text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

let modalEl = null;
function showMarkdown(rawText, title = "Markdown Preview") {
  ensureStyles();

  if (!modalEl) {
    modalEl = document.createElement("div");
    modalEl.className = "simplechat-md-modal";
    modalEl.innerHTML = `
      <header>
        <div class="title"></div>
        <div class="actions">
          <button data-action="copy">Copy</button>
          <button data-action="close">Close</button>
        </div>
      </header>
      <div class="simplechat-md-body"></div>
    `;
    document.body.appendChild(modalEl);
    modalEl.querySelector('button[data-action="close"]').addEventListener("click", () => {
      modalEl.remove();
      modalEl = null;
    });
    modalEl.querySelector('button[data-action="copy"]').addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(modalEl.__rawText || "");
      } catch (e) {
        console.warn("Clipboard copy failed", e);
      }
    });
  }

  modalEl.__rawText = rawText || "";
  modalEl.querySelector(".title").textContent = title;

  const body = modalEl.querySelector(".simplechat-md-body");
  const hasLibs = window.marked && window.DOMPurify;
  if (hasLibs) {
    const html = window.DOMPurify.sanitize(window.marked.parse(rawText || ""));
    body.innerHTML = html;
  } else {
    body.innerHTML = `<pre>${escapeHtml(rawText || "")}</pre>`;
  }
}

app.registerExtension({
  name: EXT_NAME,
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== "SimpleChatMarkdownPreview") return;

    // Ensure libraries are loaded once; if it fails, we fall back to plain text
    ensureMarkdownLibs().catch((e) => console.warn("[SimpleChat] markdown libs load failed:", e));

    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      onExecuted?.apply(this, [message]);
      const text = (message?.text && message.text.length) ? message.text[0] : "";
      showMarkdown(text, "SimpleChat Markdown Preview");
    };
  },
});

