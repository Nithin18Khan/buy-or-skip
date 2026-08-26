# AGENTS.md — Buy or Skip (adult affiliate)

Standalone Cursor project. **Not** Kids Edu Shorts. **Not** gaming.

## Brand

| | |
|--|--|
| Channel | **Buy or Skip** |
| Handle | `@BuyOrSkip` |
| Promise | Adult tool reviews. One verdict: buy, wait, or skip. |
| Floor | ₹40 lakh in 12–18 months if traffic is high-intent |
| Stretch | $1,000,000 over ~4 years |
| Upload stop | Combined ads + affiliate ≥ `$1,000,000` (`config/growth.json` `stop_uploads_at_usd`) |

## Walls

1. Never copy OAuth from kids-edu-shorts or the gaming repo
2. `made_for_kids` is always false
3. Description starts with the commission disclosure
4. One primary affiliate offer per video


## Hard walls

1. Never copy OAuth or GitHub secrets from `kids-edu-shorts` or the gaming repo
2. Never set `made_for_kids: true`
3. Every video description starts with an affiliate disclosure
4. No kids content, no loan spam, no fake get-rich-quick

## Entry

```powershell
python main.py --check
python main.py --status
python main.py --check-links
python main.py --plan-90
python main.py --episode scripts/episodes/ep_001_hostinger_vs_cheap_hosting.json --dry-run
python main.py --next
```

YouTube upload: OAuth in `credentials/` after a **new** Desktop/Web client named for this channel. GitHub secrets stay in **this** repo only.
