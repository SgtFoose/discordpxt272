# UPTIMEROBOT SETUP CHECKLIST

## ✅ Controleer je UptimeRobot instellingen:

1. **Login**: https://uptimerobot.com/dashboard
2. **Controleer Monitor**:
   - URL: https://collective-wildebeest-discordpxt272-f4306de1.koyeb.app/health
   - Interval: **5 minuten** (niet langer!)
   - Type: HTTP(s)
   - Status: Actief/Paused?

## ⚠️ Veelvoorkomende problemen:

1. **Monitor staat op "Paused"** - Zet hem op actief
2. **Interval te lang** - Moet 5 minuten zijn, niet 30 minuten
3. **Verkeerde URL** - Moet eindigen op `/health`
4. **Account limiet** - Gratis account heeft 50 monitors max

## 🔧 Alternatieve oplossingen:

### Optie 1: Cron-job.org (Gratis)
1. Ga naar: https://cron-job.org/
2. Maak account aan
3. Maak nieuwe cron job:
   - URL: https://collective-wildebeest-discordpxt272-f4306de1.koyeb.app/health
   - Interval: */5 * * * * (elke 5 minuten)

### Optie 2: Pingdom (Gratis tier)
1. Ga naar: https://www.pingdom.com/
2. Maak gratis account
3. Add check voor je URL

## 🧪 Test nu:
Bezoek: https://collective-wildebeest-discordpxt272-f4306de1.koyeb.app/
Je zou moeten zien: "Self-ping active every 20 minutes"

## 📊 Monitoring:
- Status page: https://stats.uptimerobot.com/zxDtL1vced
- Check of er daadwerkelijk pings binnenkomen