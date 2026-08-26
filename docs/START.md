# Start Buy or Skip (you do this)

Kids Edu Shorts / YouTube Channel English stays on its own GitHub job. Do not mix secrets.

## 1. Create the YouTube brand

Same Google account is OK. New brand only.

1. Open [YouTube](https://www.youtube.com)
2. Photo → **Switch account** → **Create a channel**
3. Name: **Buy or Skip**
4. Turn **Made for Kids** off
5. Copy Studio URL (`…/channel/UC…`) into `config/channel.json` → `youtube_channel_id`

Never use YouTube Channel English, Malayalam, or gaming for this factory.

## 2. New OAuth client

Google Cloud `way finder` → Credentials → Create **Web application** named `Buy or Skip`

Redirect URI:

```
https://developers.google.com/oauthplayground
```

Switch YouTube to **Buy or Skip** first, then [OAuth Playground](https://developers.google.com/oauthplayground) with **this** client. Scopes:

- `youtube.upload`
- `youtube.readonly`
- `yt-analytics.readonly` (needed for the $1M stop)

Secrets go in the **buy-or-skip** GitHub repo only:

- `YOUTUBE_CLIENT_SECRET_JSON`
- `YOUTUBE_REFRESH_TOKEN`
- Optional: `AFFILIATE_HOSTINGER_URL`, `AFFILIATE_CANVA_URL`, `AFFILIATE_NORDVPN_URL`

Never paste kids-repo secrets here.

## 3. Affiliate programs (current official URLs)

Factory probes these every run (`python main.py --check-links`):

- Hostinger join: https://www.hostinger.com/affiliates — signup: https://affiliates.hostinger.com/signup
- Canva: affiliate access is **Canvassador**, not the old `/affiliates/` page — https://www.canva.com/help/canva-affiliate-marketing-program/ and https://public.canva.site/canvassadors
- NordVPN: https://nordvpn.com/affiliate/ — dashboard: https://affiliates.nordvpn.com/
- Amazon.in (side bucket): https://affiliate-program.amazon.in/

Paste your **personal tracking URL** into `config/affiliates.json` → `tracking_urls` or the GitHub secrets above. The factory cannot mint those IDs.

Update GitHub variable `AFFILIATE_REVENUE_USD` from those dashboards. YouTube ads fill themselves after YPP.

Uploads **keep going until ads + affiliate ≥ $1,000,000**, then stop.

## 4. Factory

```powershell
cd $env:USERPROFILE\OneDrive\Desktop\money-tools-yt
python main.py --status
python main.py --check-links
python main.py --next
```

GitHub runs Monday + Thursday 06:30 IST. After 24 episodes, add more unique JSON until the $1M gate trips.
