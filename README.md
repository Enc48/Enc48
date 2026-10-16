# Thomas Vincent

Full-stack developer in Indonesia (WIB). I build and operate production systems — mostly the
unglamorous half: routing, proxying, quota accounting, and the observability that tells you which
of them broke at 3am.

## What I work on

**[9router-go](https://github.com/luqman-v1/9router-go)** — contributions to a single-binary Go
gateway that routes LLM traffic across providers: per-route body limits, usage-history index
scans, combo fallback for models that cannot hold a request, Muse Spark output-budget floors, and
an SSRF guard that no longer refuses the operator's own loopback proxy
([PR #355](https://github.com/luqman-v1/9router-go/pull/355)).

**Self-hosted AI routing** — a gateway I run with dozens of provider connections, fallback combos,
quota tracking, and edge relays on Cloudflare Workers / Vercel / Netlify for egress control.

**Local-first tooling** — Android/Termux as a real deployment target: Go builds, SQLite, long-lived
daemons, no laptop required.

## Toolbox

`Go` · `TypeScript` · `Svelte` · `Node.js` · `SQLite` · `Docker` · `Cloudflare Workers` · `Linux / Termux`

## Elsewhere

- Website — [tvpmw.id](https://tvpmw.id)

---

<sub>Open to interesting problems.</sub>