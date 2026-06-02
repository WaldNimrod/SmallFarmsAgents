# Running **Tasks** and local servers — Cursor **3.x** (Layout: **glass**)

This repo defines VS Code–compatible tasks in [`.vscode/tasks.json`](../../.vscode/tasks.json).

Target environment example: **Cursor 3.0.12**, **VS Code engine 1.105.x**, **Layout: glass**, **Stable** (2026-04). In this layout, shortcuts and the top “command” surface are **not identical** to older Cursor / plain VS Code.

---

## 1. Cursor 3 + Glass — why **Cmd+Shift+P** feels “new”

On recent Cursor builds, **Cmd+Shift+P** may open the **unified / glass command surface** (Agent-oriented) instead of the classic **Command Palette** list you remember from VS Code.

That does **not** remove Tasks — it changes **how you open the palette that lists them**.

**Practical ways to run a Task:**

| Method | Notes |
|--------|--------|
| **Menu: Terminal → Run Task…** | Still wired in the Electron app; opens the **same task picker** as `Tasks: Run Task`. **Most reliable** on Glass. |
| **Classic Command Palette** | Try **F1** (on many Mac keyboards: **Fn+F1**) — often still bound to **Show All Commands** in the VS Code core. Then type **`Run Task`** or **`Tasks: Run Task`**. |
| **Help menu** | Look for **Show All Commands** / **Command Palette** (wording varies slightly by build). |
| **Keyboard Shortcuts** | **Cmd+K** then **Cmd+S** → search **`Tasks: Run Task`** (see current binding); search what **`Cmd+Shift+P`** is bound to (may be a `cursor…` / Agent command) and optionally **rebind** palette vs Agent. |
| **Default build task** | **Cmd+Shift+B** → **Run Build Task**. In this repo the default build is **“🟢 Admin Dashboard — Start”** (`tasks.json`: `group.kind: "build"`, `isDefault: true`). |

**Terminal fallback (always works):**

```bash
bash scripts/admin_server.sh start    # or: run
bash scripts/restart_all_servers.sh run
```

---

## 2. Task list (summary)

| Task label | Effect |
|------------|--------|
| 🟢 Admin Dashboard — Start | `admin_server.sh start` → **http://127.0.0.1:5001** |
| 🔴 Admin Dashboard — Stop | stop admin |
| 🔄 Admin Dashboard — Restart | restart admin |
| 📋 Admin Dashboard — Status | status |
| 🟢 Public Viewer — Start | `viewer_server.sh start` → **http://127.0.0.1:8081** |
| 🚀 כל השרתים — Start (run) | start admin + viewer |
| 🔄 כל השרתים — Restart All | restart both |

---

## 3. Cursor **Browser / Preview** shows **403** on `http://127.0.0.1:5001`

If the **embedded browser** or **Preview** pane shows **403** (or “private network” / “page isn’t working”) while `curl` or an **external** browser works:

- The **Flask admin app** does not normally return **403** for `/` (dashboard route).
- Cursor’s embedded Chromium may **restrict or proxy loopback** (`127.0.0.1`) differently than Safari/Chrome — **403 there is often a Preview limitation**, not proof the server is wrong.

**Verify with:**

```bash
curl -sI http://127.0.0.1:5001/
```

**Use the admin UI in a normal browser:**

```bash
open http://127.0.0.1:5001    # macOS
```

---

## 4. Logs and PIDs

- `.run/admin_server.pid`, `.run/admin_server.log`
- `.run/viewer_server.pid`, `.run/viewer_server.log`

See also [`README.md`](README.md) in this folder.
