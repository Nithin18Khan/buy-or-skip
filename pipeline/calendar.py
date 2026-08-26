"""24 unique long-form scripts for the first 90 days (2 per week)."""

from __future__ import annotations

import json
from pathlib import Path

CHANNEL = "Buy or Skip"
DISCLOSURE = (
    "This video contains affiliate links. I may earn a commission if you buy, "
    "at no extra cost to you."
)

# Extra unique spoken beats so two episodes never share the same middle.
BEATS = {
    "ep_001_hostinger_vs_cheap_hosting": (
        "This is for someone launching a real site this month, not collecting free subdomains.",
        "The homepage price is a tease. Ask what month thirteen costs after the promo.",
        "Cheap panels die when traffic spikes or when you need a human, not a chatbot.",
        "Skip Hostinger if you need enterprise SLAs or a dedicated ops team. Buy if you want a clean panel and a price that still makes sense after the sale banner dies.",
    ),
    "ep_002_canva_pro_worth_it": (
        "This is for people who ship graphics on a schedule: thumbnails, ads, pitch decks.",
        "Pro looks cheap until you forget to cancel the annual plan you do not use.",
        "Free Canva blocks Brand Kit and treats background remover like a drip.",
        "Skip Pro if you design twice a year. Buy if Canva is already your job, not a toy.",
    ),
    "ep_003_nordvpn_vs_free_vpn": (
        "This is for travel Wi-Fi, hotels, and shared networks. Not for cosplay hacking.",
        "Free VPNs are free because you are the product. NordVPN is a bill.",
        "A VPN does not make you invisible. It encrypts a hop. Logs and jurisdiction still matter.",
        "Skip Nord if you only browse at home on fiber. Buy if you work from cafes and airports.",
    ),
    "ep_004_chatgpt_plus_vs_free": (
        "This is for people who already hit the free cap during work hours.",
        "Plus is twenty dollars of queue-jumping. It is not a genius implant.",
        "It still hallucinates citations. Paying does not make the model honest.",
        "Skip Plus if you dabble on weekends. Buy if waiting on a spinner costs you clients.",
    ),
    "ep_005_notion_vs_google_docs": (
        "This is for a one-person shop that needs a wiki plus a tracker.",
        "Notion is free until your workspace becomes a maze you pay to maintain.",
        "Docs wins comments. Notion wins databases. Neither replaces a real CRM by magic.",
        "Skip Notion if you only write letters. Stay on Docs. Buy Notion when the pipeline is the product.",
    ),
    "ep_006_capcut_desktop_vs_phone": (
        "This is for editors who think the phone app is the whole product.",
        "Mobile exports lie about bitrate. Desktop is where the timeline is real.",
        "Phone CapCut is fine for stories. It chokes on multi-cam and long VO.",
        "Skip desktop if you only post Stories. Buy the desktop habit if this is income.",
    ),
    "ep_007_semrush_vs_ubersuggest": (
        "This is for a new site that needs keywords, not a full agency cockpit.",
        "Semrush can bill like a staff member. Ubersuggest is the cheaper report stack.",
        "You do not need every module on day one. Keyword plus audit is the job.",
        "Skip Semrush until content is shipping weekly. Buy Ubersuggest or a single Semrush kit when you have pages to rank.",
    ),
    "ep_008_midjourney_vs_free_ai_images": (
        "This is for thumbnail makers, not art-school arguments.",
        "Midjourney is a subscription. Free models cost you time and cleanup.",
        "Canva Magic sits in the middle: faster, less control, good enough for many thumbs.",
        "Skip Midjourney if you cannot prompt. Buy it when unique stills are the channel look.",
    ),
    "ep_009_cursor_vs_vscode": (
        "This is for people who already write code. Not for prompt tourists.",
        "Cursor is VS Code plus an agent bill. VS Code stays free.",
        "The agent will still invent APIs. You still read the diff.",
        "Skip Cursor if you paste homework. Buy it if review time is the bottleneck.",
    ),
    "ep_010_descript_vs_capcut": (
        "This is for talking-head creators who hate cutting uhms on a timeline.",
        "Descript bills like software. CapCut is cheaper if you already live there.",
        "Text-based edit is magic until you need B-roll stacked on beats.",
        "Skip Descript if you cut music videos. Buy it if the A-roll is your face.",
    ),
    "ep_011_elevenlabs_vs_free_tts": (
        "This is for product videos that cannot sound like a car GPS.",
        "ElevenLabs sells a voice. Free TTS is a placeholder.",
        "A pretty voice still reads a bad script. Pay for voice after the words are true.",
        "Skip ElevenLabs for internal drafts. Buy it when the voice is on the internet forever.",
    ),
    "ep_012_runway_vs_capcut_ai": (
        "This is for people generating B-roll, not a feature film.",
        "Runway is lab pricing. CapCut AI is a consumer button with a ceiling.",
        "Both can look like sludge. Your job is to throw away the sludge.",
        "Skip Runway if CapCut already gets a usable four seconds. Buy Runway when you need control.",
    ),
    "ep_013_namecheap_vs_godaddy": (
        "This is for anyone buying a first domain from an ad.",
        "GoDaddy wins the first-year screenshot and loses the renewal.",
        "Namecheap is usually the calmer invoice. Hostinger matters if you also need hosting.",
        "Skip GoDaddy upsells. Buy the registrar that does not hunt you in year two.",
    ),
    "ep_014_grammarly_vs_languagetool": (
        "This is for client email, invoices, and proposals — not novels.",
        "Grammarly Premium is a habit tax. LanguageTool is quieter.",
        "Tone nags can make you sound like a bot. That loses deals.",
        "Skip Grammarly if a browser checker is enough. Buy it only if a team shares a style.",
    ),
    "ep_015_zoom_vs_google_meet": (
        "This is for paid calls, not family gossip.",
        "Meet is free inside Gmail. Zoom still wins recordings and rooms.",
        "The wrong tool is the one that is not on your client's calendar.",
        "Skip Zoom if your whole world is Google. Buy Zoom when recordings are the deliverable.",
    ),
    "ep_016_clickup_vs_notion": (
        "This is for tasks you will actually close this week.",
        "ClickUp can become a cockpit you decorate instead of a list you finish.",
        "Notion as a task app is a wiki in a trench coat.",
        "Skip ClickUp if a paper list works. Buy it when multiple people need statuses that mean something.",
    ),
    "ep_017_shopify_vs_woocommerce": (
        "This is for a first store, not a mall.",
        "Shopify is rent. Woo is homework plus hosting — Hostinger only if you pick Woo.",
        "Apps on both sides will eat the margin if you are not watching.",
        "Skip Woo if you hate servers. Buy Shopify if speed to first sale matters more than control.",
    ),
    "ep_018_stripe_vs_paypal": (
        "This is for getting paid, not collecting logos.",
        "PayPal holds and fees surprise new sellers. Stripe is cleaner for subscriptions.",
        "The button that customers already trust will convert, even if it is uglier.",
        "Skip Stripe if your buyers only have PayPal. Buy Stripe when subscriptions are the model.",
    ),
    "ep_019_proton_vs_gmail": (
        "This is for people who sell privacy, or actually need it.",
        "Gmail is free because the graph is the product. Proton is a bill.",
        "A VPN is not a mail host. NordVPN does not replace Proton or Gmail.",
        "Skip Proton if you live in Google Calendar. Buy Proton if leak risk is a real job risk.",
    ),
    "ep_020_obsidian_vs_notion": (
        "This is for notes you might still need in ten years.",
        "Notion can lock the graph in their cloud. Obsidian files sit on disk.",
        "Pretty databases are not the same as files you can zip.",
        "Skip Obsidian if you want pretty sharing. Buy it if ownership is the feature.",
    ),
    "ep_021_riverside_vs_zoom_record": (
        "This is for podcasts and interviews where audio is the product.",
        "Zoom is convenient and compressed. Riverside is local tracks and a bill.",
        "If you transcribe garbage in, you edit garbage all week.",
        "Skip Riverside for internal standups. Buy it when the episode is public.",
    ),
    "ep_022_epidemic_vs_yt_audio_library": (
        "This is for people who publish on a clock.",
        "YouTube's library is free and overused. Epidemic is a subscription for fresh beds.",
        "A copyright claim costs more than a month of music.",
        "Skip Epidemic if you post monthly. Buy it if daily uploads need new beds.",
    ),
    "ep_023_convertkit_vs_mailchimp": (
        "This is for a tiny list you will actually email.",
        "Mailchimp got expensive for creators. ConvertKit is built around a list.",
        "Eighty subscribers do not need an enterprise automation tree.",
        "Skip both if you have no list. Buy ConvertKit when the email is the business.",
    ),
    "ep_024_bluehost_vs_hostinger": (
        "This is for WordPress people still living in 2014 ads.",
        "Bluehost is famous. Hostinger is often the calmer 2026 invoice.",
        "Compare renewals, disk, and support — not the first-month coupon.",
        "Skip Bluehost if the renewal is a jump scare. Buy Hostinger if the panel and price still make sense in month thirteen.",
    ),
}

EPISODES = [
    ("ep_001_hostinger_vs_cheap_hosting", "hostinger", "Is Hostinger actually cheaper than budget hosting?", "Cheap hosting looks cheap until support and speed collapse. Hostinger is the tool we test against a no-name plan. I show what you get for the money, where it breaks, and who should skip it."),
    ("ep_002_canva_pro_worth_it", "canva", "Is Canva Pro worth paying for?", "Free Canva is enough for a school poster. Pro is for people who ship thumbnails every week. We compare Brand Kit, background remover, and Magic Studio against the free tier."),
    ("ep_003_nordvpn_vs_free_vpn", "nordvpn", "Free VPN vs NordVPN — what actually leaks?", "Free VPNs often sell your traffic. NordVPN is the paid baseline. This is a practical test for travel Wi-Fi and public networks, not a fear ad."),
    ("ep_004_chatgpt_plus_vs_free", "amazon_in", "ChatGPT Plus vs free: who should pay?", "Free ChatGPT is slower and capped. Plus is a time buy. We time real tasks: rewrite, code stub, and research, then say when paying is stupid."),
    ("ep_005_notion_vs_google_docs", "amazon_in", "Notion vs Google Docs for a one-person business", "Docs wins at comments. Notion wins at databases. If you only write letters, stay on Docs. If you run a pipeline, Notion starts to pay rent."),
    ("ep_006_capcut_desktop_vs_phone", "amazon_in", "CapCut desktop vs phone: which should editors use?", "Phone CapCut is fast. Desktop is the real cut. We edit the same 60-second promo on both and show where mobile lies to you."),
    ("ep_007_semrush_vs_ubersuggest", "hostinger", "Semrush vs Ubersuggest for a new site", "You do not need every Semrush module on day one. We pick keyword + site audit only, then compare Ubersuggest’s cheaper reports."),
    ("ep_008_midjourney_vs_free_ai_images", "canva", "Midjourney vs free AI images for YouTube thumbs", "Free image models are noisy. Midjourney is spendy. Canva Magic Studio sits in the middle. We make three thumbnails and pick a stack."),
    ("ep_009_cursor_vs_vscode", "amazon_in", "Cursor vs VS Code if you already code", "VS Code is free and everywhere. Cursor is VS Code plus an agent. This is for people who already type, not for ‘AI will replace you’ hype."),
    ("ep_010_descript_vs_capcut", "amazon_in", "Descript vs CapCut for talking-head edits", "Descript edits text like a doc. CapCut edits a timeline. If you record yourself, Descript can cut uhms faster. If you cut B-roll, CapCut still wins."),
    ("ep_011_elevenlabs_vs_free_tts", "amazon_in", "ElevenLabs vs free TTS for product videos", "Free TTS sounds like a GPS. ElevenLabs sells a voice. We A/B the same script and talk about when the extra money is wasted."),
    ("ep_012_runway_vs_capcut_ai", "canva", "Runway vs CapCut AI video tools", "Runway is a lab. CapCut AI is a consumer button. We generate the same 4-second clip both ways and keep the one that does not look like sludge."),
    ("ep_013_namecheap_vs_godaddy", "hostinger", "Namecheap vs GoDaddy: stop overpaying for a domain", "GoDaddy ads make domains look cheaper than renewals. We compare first-year vs year-two price, then where Hostinger sits if you also need hosting."),
    ("ep_014_grammarly_vs_languagetool", "amazon_in", "Grammarly vs LanguageTool for client email", "Grammarly nags. LanguageTool is quieter. If you send invoices, tone matters more than a premium upsell."),
    ("ep_015_zoom_vs_google_meet", "amazon_in", "Zoom vs Google Meet for client calls", "Meet is free if you already live in Gmail. Zoom still wins recordings and breakout rooms. Pick from your calendar, not from ads."),
    ("ep_016_clickup_vs_notion", "amazon_in", "ClickUp vs Notion for tasks you will actually do", "ClickUp is a cockpit. Notion is a wiki. If your board has 12 statuses you never touch, you bought a toy."),
    ("ep_017_shopify_vs_woocommerce", "hostinger", "Shopify vs WooCommerce for a first store", "Shopify is rent. WooCommerce is homework plus hosting. Hostinger only matters if you pick Woo. We cost out 12 months."),
    ("ep_018_stripe_vs_paypal", "amazon_in", "Stripe vs PayPal for getting paid", "PayPal is everywhere. Stripe is cleaner for subscriptions. Fees and holds matter more than the logo on the button."),
    ("ep_019_proton_vs_gmail", "nordvpn", "Proton vs Gmail if privacy is the product", "Gmail is the default. Proton is the lock. NordVPN does not replace either. We say who should move and who is performing privacy."),
    ("ep_020_obsidian_vs_notion", "amazon_in", "Obsidian vs Notion for notes you own", "Obsidian files live on disk. Notion lives in their cloud. If you write for years, that difference is the review."),
    ("ep_021_riverside_vs_zoom_record", "amazon_in", "Riverside vs Zoom for podcast recording", "Zoom recordings are convenient and compressed. Riverside is local tracks. If audio is the product, pay for tracks."),
    ("ep_022_epidemic_vs_yt_audio_library", "amazon_in", "Epidemic Sound vs YouTube Audio Library", "YouTube’s library is free and overused. Epidemic is a subscription for people who publish daily. We match three moods."),
    ("ep_023_convertkit_vs_mailchimp", "amazon_in", "ConvertKit vs Mailchimp for a tiny list", "Mailchimp got expensive for creators. ConvertKit is built around a list you actually email. If you have 80 subscribers, keep it simple."),
    ("ep_024_bluehost_vs_hostinger", "hostinger", "Bluehost vs Hostinger in 2026", "Bluehost is famous from old WordPress ads. Hostinger is the current budget pick. We compare renewals, not the homepage sale price."),
]


def _body(eid: str, title: str, blurb: str, program: str) -> dict:
    hook = blurb.split(". ")[0].rstrip(".") + "."
    who, price, brk, verdict = BEATS[eid]
    narration = [
        f"{CHANNEL}. Adult tool reviews. One verdict. Buy, wait, or skip.",
        hook,
        DISCLOSURE,
        blurb,
        who,
        price,
        brk,
        verdict,
        "The description has one tracking link for this video. One offer. Not a dump of twenty tools.",
        f"This is {CHANNEL}. English. Eighteen plus. Not for children.",
    ]
    return {
        "title": title,
        "youtube_title": title[:90],
        "channel": CHANNEL,
        "language": "en",
        "made_for_kids": False,
        "verdict_prompt": "BUY, WAIT, or SKIP",
        "affiliate": {
            "program": program,
            "tracking_url": "",
        },
        "tags": ["review", "tools", "BuyOrSkip", program, "english"],
        "narration": narration,
        "description": (
            f"{DISCLOSURE}\n\n{title}\n\n{blurb}\n\n"
            f"{who}\n{price}\n{brk}\n{verdict}\n\n"
            f"Channel: {CHANNEL} (@BuyOrSkip)\n"
            "Adult tool review. English. Not for children.\n"
            "Paste your real affiliate.tracking_url in the episode JSON before upload."
        ),
        "shots": [
            {"id": "hook", "label": "HOOK", "line": hook},
            {"id": "who", "label": "WHO IT IS FOR", "line": who},
            {"id": "price", "label": "REAL PRICE", "line": price},
            {"id": "catch", "label": "THE CATCH", "line": brk},
            {"id": "verdict", "label": "VERDICT", "line": verdict},
            {"id": "end", "label": CHANNEL.upper(), "line": "One link. One offer."},
        ],
    }


def write_90_day(root: Path) -> Path:
    ep_dir = root / "scripts" / "episodes"
    ep_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i, (eid, program, title, blurb) in enumerate(EPISODES, start=1):
        week = (i + 1) // 2
        body = _body(eid, title, blurb, program)
        body["id"] = eid
        body["week"] = week
        body["slot"] = "long"
        path = ep_dir / f"{eid}.json"
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("lock_script"):
                manifest.append(
                    {
                        "id": eid,
                        "file": str(path.relative_to(root)).replace("\\", "/"),
                        "title": str(existing.get("title") or title),
                        "program": program,
                        "week": week,
                    }
                )
                continue
        path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
        manifest.append({"id": eid, "file": str(path.relative_to(root)).replace("\\", "/"), "title": title, "program": program, "week": week})
    man_path = root / "scripts" / "calendar" / "90day.json"
    man_path.parent.mkdir(parents=True, exist_ok=True)
    man_path.write_text(
        json.dumps({"days": 90, "long_videos": len(manifest), "cadence": "2 long / week", "episodes": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )
    return man_path
