# Access Your Raspberry Pi from Your Phone

## One-Time Setup

### 1. Install Tailscale on Your Phone
- **iPhone**: Download from the App Store
- **Android**: Download from Google Play Store
- Search for "Tailscale"

### 2. Sign In to Tailscale
- Open the Tailscale app
- Tap "Log In" or "Get Started"
- Choose the same login method you used on your Pi (Google, GitHub, Microsoft, etc.)
- Authorize the app when prompted

### 3. Find Your Pi
- In the Tailscale app, you'll see a list of devices
- Look for your Raspberry Pi (it will have a name like `raspberrypi` or similar)
- Note the address shown (either `100.x.x.x` or `pi-name.tailnet-name.ts.net`)

## Accessing the Vino Temperature Control App

### Option A: Using the Tailscale IP Address
1. Open your phone's web browser (Safari, Chrome, etc.)
2. Type in the address bar: `http://100.x.x.x:5000`
   - Replace `100.x.x.x` with the actual IP shown in your Tailscale app
3. The Vino Temperature Control interface should load

### Option B: Using the Tailscale Hostname (easier to remember)
1. Open your phone's web browser
2. Type: `http://your-pi-name.ts.net:5000`
   - Replace `your-pi-name` with the actual hostname shown in Tailscale
3. The app should load

## Troubleshooting

### "Can't connect" or "Site not reachable"
- Check that Tailscale is connected (green indicator in the app)
- Verify the Pi is powered on and connected to Wi-Fi
- Make sure you're using port `:5000` in the URL
- Try switching between Wi-Fi and mobile data on your phone

### "Connection refused"
- The app might be bound to localhost only. Contact support to reconfigure.

### Slow loading
- This is normal when off your home Wi-Fi; Tailscale routes through the internet

## Security Notes
- **Always connected**: Leave Tailscale running in the background for instant access
- **Secure by default**: Only you can access your Pi (no one else can connect)
- **No exposed ports**: Your home router doesn't need any port forwarding
- **Works anywhere**: Coffee shop, work, vacation—anywhere with internet

## Quick Reference
- **Pi Address**: `100.x.x.x:5000` or `your-pi-name.ts.net:5000`
- **Tailscale App**: Use to check connection status and view your Pi's current address
- **Web Browser**: Any browser works (Safari, Chrome, Firefox, Edge)

---

**Need Help?**
- Tailscale support: https://tailscale.com/contact/support
- Check Pi status in Tailscale app (shows "Last seen" timestamp)
