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

Switch YouTube to **Buy or Skip** first, then [OAuth Playground](https://developers.google.com/oauthplayground) with **this** client. Scopes: `youtube.upload` + `youtube.readonly`.

Secrets go in a **new** GitHub repo for this folder, names:

- `YOUTUBE_CLIENT_SECRET_JSON`
- `YOUTUBE_REFRESH_TOKEN`

Never paste kids-repo secrets here.

## 3. Affiliate programs (join, then paste links)

- [Hostinger](https://www.hostinger.com/affiliates)
- [Canva](https://www.canva.com/affiliates/)
- [NordVPN](https://nordvpn.com/affiliates/)
- [Amazon.in](https://affiliate-program.amazon.in/) as a side bucket only

Put your tracking URL in each episode JSON: `affiliate.tracking_url`

## 4. Factory

```powershell
cd $env:USERPROFILE\OneDrive\Desktop\money-tools-yt
python main.py --next
```

GitHub will run Monday + Thursday 06:30 IST after this folder is a repo with those secrets.
