# External Keep-Alive Solutions for Koyeb

## Option 1: UptimeRobot (Recommended - Free)
1. Go to https://uptimerobot.com/
2. Create a free account
3. Add a new monitor:
   - Monitor Type: HTTP(s)
   - URL: https://your-koyeb-app-url/health
   - Monitoring Interval: 5 minutes
   - Alert Contacts: Your email

## Option 2: Pingdom (Free tier available)
1. Go to https://www.pingdom.com/
2. Sign up for free account
3. Create HTTP check for your Koyeb URL

## Option 3: Better Uptime (Free tier)
1. Go to https://betteruptime.com/
2. Create monitor for your service

## Option 4: Self-Hosted Cron Job
If you have another server or VPS, add this to crontab:
```bash
*/5 * * * * curl -s https://your-koyeb-app-url/health > /dev/null 2>&1
```

## Your Koyeb URL
Your service URL should be something like:
https://your-app-name-your-username.koyeb.app

## Current Implementation
The updated keep_alive.py now includes:
- Self-pinging every 25 minutes
- /ping endpoint for external monitoring
- Timestamps to track activity
- Health check endpoint at /health

## Testing
Visit your Koyeb URL in browser to see if the keep-alive page loads.
The /health endpoint should return "OK" for monitoring services.