const STORAGE_KEY = "techcorp-ai-chat-history";

const state = {
  conversations: [],
  currentId: null,
  sending: false,
  copiedId: null,
};

const els = {
  list: document.getElementById("conversationList"),
  messages: document.getElementById("messages"),
  title: document.getElementById("conversationTitle"),
  status: document.getElementById("statusPill"),
  generation: document.getElementById("generationIndicator"),
  error: document.getElementById("errorBar"),
  form: document.getElementById("composer"),
  input: document.getElementById("messageInput"),
  send: document.getElementById("sendButton"),
  newChat: document.getElementById("newChatButton"),
};

function uid() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function createConversation() {
  const conversation = {
    id: uid(),
    title: "Nouvelle conversation",
    messages: [],
    createdAt: new Date().toISOString(),
  };
  state.conversations.unshift(conversation);
  state.currentId = conversation.id;
  clearError();
  persist();
  render();
}

function currentConversation() {
  return state.conversations.find((item) => item.id === state.currentId) || state.conversations[0];
}

function load() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (stored?.conversations?.length) {
      state.conversations = stored.conversations;
      state.currentId = stored.currentId || stored.conversations[0].id;
      return;
    }
  } catch {
    localStorage.removeItem(STORAGE_KEY);
  }
  createConversation();
}

function persist() {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      conversations: state.conversations.slice(0, 30),
      currentId: state.currentId,
    }),
  );
}

function escapeText(value) {
  const div = document.createElement("div");
  div.textContent = value;
  return div.innerHTML;
}

function formatDate(value) {
  try {
    return new Intl.DateTimeFormat("fr-FR", { day: "2-digit", month: "2-digit" }).format(new Date(value));
  } catch {
    return "";
  }
}

function renderList() {
  els.list.innerHTML = "";
  state.conversations.forEach((conversation) => {
    const row = document.createElement("div");
    row.className = "conversation-row";

    const button = document.createElement("button");
    button.className = "conversation-button";
    button.type = "button";
    button.setAttribute("aria-current", conversation.id === state.currentId ? "true" : "false");
    button.innerHTML = `
      <span class="conversation-title">${escapeText(conversation.title)}</span>
      <span class="conversation-date">${formatDate(conversation.createdAt)}</span>
    `;
    button.addEventListener("click", () => {
      state.currentId = conversation.id;
      clearError();
      persist();
      render();
    });

    const del = document.createElement("button");
    del.className = "delete-button";
    del.type = "button";
    del.textContent = "Supprimer";
    del.setAttribute("aria-label", `Supprimer ${conversation.title}`);
    del.addEventListener("click", () => deleteConversation(conversation.id));

    row.append(button, del);
    els.list.append(row);
  });
}

function deleteConversation(id) {
  state.conversations = state.conversations.filter((item) => item.id !== id);
  if (!state.conversations.length) {
    createConversation();
    return;
  }
  if (state.currentId === id) {
    state.currentId = state.conversations[0].id;
  }
  clearError();
  persist();
  render();
}

function renderMessages() {
  const conversation = currentConversation();
  els.title.textContent = conversation?.title || "Nouvelle conversation";
  els.messages.innerHTML = "";

  if (!conversation?.messages.length) {
    els.messages.innerHTML = `
      <div class="empty-state">
        <h3>Aucune analyse en cours</h3>
        <p>Les reponses sont volontairement courtes. Demandez plus de detail si necessaire.</p>
      </div>
    `;
    return;
  }

  conversation.messages.forEach((message) => {
    els.messages.append(renderMessage(message));
  });
  scrollToBottom();
}

function renderMessage(message) {
  const article = document.createElement("article");
  article.className = `message ${message.role}${message.error ? " error" : ""}`;

  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.textContent = message.role === "user" ? "Vous" : "Conseiller";

  const body = document.createElement("div");
  body.className = "message-body";
  body.innerHTML = message.loading
    ? '<span class="inline-loading">Preparation de la reponse</span>'
    : escapeText(message.content);

  const wrap = document.createElement("div");
  wrap.className = "message-wrap";
  wrap.append(meta, body);

  if (message.role === "assistant" && !message.loading && !message.error) {
    const actions = document.createElement("div");
    actions.className = "message-actions";

    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "copy-button";
    copy.textContent = state.copiedId === message.id ? "Copie" : "Copier";
    copy.addEventListener("click", () => copyMessage(message.id, message.content));

    actions.append(copy);
    wrap.append(actions);
  }

  article.append(wrap);
  return article;
}

function render() {
  renderList();
  renderMessages();
  els.send.disabled = state.sending;
  els.generation.hidden = !state.sending;
}

function scrollToBottom() {
  els.messages.scrollTop = els.messages.scrollHeight;
}

function updateAssistantMessage(id, content, loading = false) {
  const conversation = currentConversation();
  const message = conversation.messages.find((item) => item.id === id);
  if (!message) return;
  message.content = content;
  message.loading = loading;
  persist();
  renderMessages();
}

function appendMessage(message) {
  const conversation = currentConversation();
  conversation.messages.push({ id: uid(), createdAt: new Date().toISOString(), ...message });
  if (message.role === "user" && conversation.title === "Nouvelle conversation") {
    conversation.title = message.content.replace(/\s+/g, " ").slice(0, 54) || conversation.title;
  }
  persist();
  render();
  return conversation.messages[conversation.messages.length - 1].id;
}

function requestMessages(conversation) {
  return conversation.messages
    .filter((message) => !message.loading && !message.error)
    .map((message) => ({ role: message.role, content: message.content }));
}

async function sendMessage(event) {
  event.preventDefault();
  const text = els.input.value.trim();
  if (!text || state.sending) return;

  clearError();
  const conversation = currentConversation();
  appendMessage({ role: "user", content: text });
  els.input.value = "";
  resizeInput();

  const assistantId = appendMessage({ role: "assistant", content: "", loading: true });
  state.sending = true;
  render();

  try {
    await streamResponse(requestMessages(conversation), assistantId);
  } catch (error) {
    const message = friendlyError(error);
    updateAssistantMessage(assistantId, message, false);
    const assistant = conversation.messages.find((item) => item.id === assistantId);
    if (assistant) assistant.error = true;
    showError(message);
  } finally {
    state.sending = false;
    persist();
    render();
  }
}

async function streamResponse(messages, assistantId) {
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  if (!response.ok) {
    throw new Error(await responseError(response));
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let fullText = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const rawEvent of events) {
      const parsed = parseSse(rawEvent);
      if (!parsed) continue;
      if (parsed.event === "token") {
        fullText += parsed.data.content || "";
        updateAssistantMessage(assistantId, fullText, false);
      }
      if (parsed.event === "error") {
        throw new Error(parsed.data.message || "Erreur du serveur.");
      }
    }
  }

  updateAssistantMessage(assistantId, fullText.trim() || "Aucune reponse recue.", false);
}

async function responseError(response) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (data.detail?.message) return data.detail.message;
    if (data.detail?.code === "blocked_security_policy") return "Message bloque par la politique de securite.";
  } catch {
    return response.statusText || `HTTP ${response.status}`;
  }
  return response.statusText || `HTTP ${response.status}`;
}

function friendlyError(error) {
  const message = String(error?.message || error || "");
  if (message.includes("Ollama is not reachable")) {
    return "Le moteur local Ollama est indisponible. Verifiez qu'il est demarre.";
  }
  if (message.includes("HTTP 404")) {
    return "Le modele Ollama configure est introuvable. Recreez le modele techcorp-phi35-financial.";
  }
  return message || "Une erreur est survenue pendant la generation.";
}

function parseSse(rawEvent) {
  const lines = rawEvent.split("\n");
  const eventLine = lines.find((line) => line.startsWith("event:"));
  const dataLine = lines.find((line) => line.startsWith("data:"));
  if (!dataLine) return null;
  return {
    event: eventLine ? eventLine.slice(6).trim() : "message",
    data: JSON.parse(dataLine.slice(5).trim()),
  };
}

async function copyMessage(id, content) {
  try {
    await navigator.clipboard.writeText(content);
    state.copiedId = id;
    renderMessages();
    setTimeout(() => {
      state.copiedId = null;
      renderMessages();
    }, 1400);
  } catch {
    showError("Copie impossible depuis ce navigateur.");
  }
}

async function checkStatus() {
  try {
    const response = await fetch("/api/status", { cache: "no-store" });
    const data = await response.json();
    if (response.ok && data.ollama_available) {
      els.status.dataset.state = "online";
      els.status.textContent = "Disponible";
    } else {
      els.status.dataset.state = "offline";
      els.status.textContent = "Indisponible";
    }
  } catch {
    els.status.dataset.state = "offline";
    els.status.textContent = "Hors ligne";
  }
}

function showError(message) {
  els.error.textContent = message;
  els.error.hidden = false;
}

function clearError() {
  els.error.textContent = "";
  els.error.hidden = true;
}

function resizeInput() {
  els.input.style.height = "auto";
  els.input.style.height = `${Math.min(els.input.scrollHeight, 160)}px`;
}

els.form.addEventListener("submit", sendMessage);
els.newChat.addEventListener("click", createConversation);
els.input.addEventListener("input", resizeInput);
els.input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    els.form.requestSubmit();
  }
});

load();
render();
resizeInput();
checkStatus();
setInterval(checkStatus, 10000);
