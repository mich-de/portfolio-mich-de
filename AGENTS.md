# MDEANGELIS Portfolio — AGENTS.md

## Stack
- Next.js 16.1 (App Router) + React 19.2 + TypeScript 5.9
- Tailwind CSS v4 (`@theme inline` directive, `@tailwindcss/postcss`)
- shadcn/ui (New York style, `components.json` at root)
- Framer Motion (page transitions in `app/template.tsx`), GSAP (hero animations)
- Zustand (state), `react-hook-form` + `zod` (contact form), `next-themes` (forced dark)
- `next/font/local` for Kamerik (display) + Unitext (sans) in `app/fonts/`

## Commands
| Command | Purpose |
|---------|---------|
| `npm run dev` | Dev server on :3000 |
| `npm run build` | Production build (output: standalone) |
| `npm run start` | Prod server |
| `npm run lint` | ESLint v9 flat config |

No tests, no typecheck script.

## Architecture
- **Single page** — `app/page.tsx` is `"use client"` with all sections rendered inline
- **Atomic design**: `components/atoms/`, `molecules/`, `organisms/`, `ui/` (shadcn primitives)
- **Path alias**: `@/*` → root (e.g. `@/components/...`, `@/lib/utils`)
- **i18n**: Client-side only, no routing. Italian default (`context/language-provider.tsx`), persisted to `localStorage`. Dictionary in `utils/dictionaries.ts`.
- **Contact**: Server action in `actions/contact.ts` with Zod validation (stub — logs to console, no real email)
- **Animations**: CSS `animation-timeline: view()` for scroll fades. Framer Motion for page transitions and micro-interactions. GSAP in hero.
- **Build output**: `output: "standalone"` in `next.config.ts` — generates self-contained `/.next/standalone/`

## Styling conventions
- Tailwind v4 uses `@theme inline { }` in `globals.css`, not `tailwind.config`
- Section H2 gradient: `from-accent via-chart-1 to-chart-3` (orange spectrum)
- Logo split: `MDE` → `font-sans` (bold), `ANGELIS` → `font-display` (light)
- `.animate-text-shine` for sparkle effect on logo; CSS vars `--shine-base` / `--shine-accent`
- `.interesse-card` class for interest cards (glassmorphism + spotlight)
- `bg-background` for consistent section backgrounds

## Quirks
- **i18n** — client-side only, no routes. `html lang="it"` hardcoded. Language persisted to `localStorage`.
- `globals.css` is single CSS entrypoint. Tailwind v4 `@theme inline` — no `tailwind.config`.
- Theme toggle exists (`atoms/theme-toggle.tsx`), uses `next-themes` with `defaultTheme="dark"`.
- Assets from `public/assets/` (transparent PNGs for icons, logo.jpg, logo_symbol_transparent.png).
- ESLint ignores: `.next/`, `out/`, `build/`, `next-env.d.ts`
- No tests, no CI, no dockerfile.

## Security (applied)
- CSP header enforced in `next.config.ts` (self + inline styles/scripts)
- `remotePatterns` restricted to `mdeangelis.me` (SSRF prevention)
- Contact form: max lengths on all fields, rate-limited (3 req/min per IP via in-memory map)
- Contact server action (`actions/contact.ts`) is a stub — logs to console, no real email
