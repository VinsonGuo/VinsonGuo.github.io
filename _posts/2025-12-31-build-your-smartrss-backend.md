---
layout: post
title: "Build Your RSS Backend for SmartRSS: A Beginner's Guide to FreshRSS, Miniflux, RSSHub, and RSS-Bridge"
author: "Vinson Guo"
categories: [tutorial, self-hosting, rss, docker, smartrss]
image: assets/img/smartrss/Screenshot_2025-12-24-10-55-32-81_bb53aaa59eb1f897861a3c681a6c04b4.jpg
---

This guide walks you through setting up a self-hosted RSS backend with **FreshRSS**, **Miniflux**, **RSSHub**, and **RSS-Bridge**, even if you've never touched a server before. They all work with SmartRSS, so your feeds stay under your control.

## Why build your own RSS backend?

You get:

- Your feeds sync across all your devices through SmartRSS
- Your reading habits stay on your own server
- No monthly fees beyond the VPS
- No limit on the number of subscriptions
- It's fast, since it runs on your own infrastructure

## What you'll need

- A VPS (Virtual Private Server) - $5-10/month
- About 30 minutes of your time
- No coding experience required!

## Quick start: try official instances first

Before setting up your own server, you can try these official demo instances:

### Official FreshRSS demo

`https://demo.freshrss.org/`

Clean interface, mobile-friendly, good API support. Good for beginners who want a traditional RSS experience.

### Official Miniflux demo
`https://miniflux.app/` (offers a free trial)

Modern design, excellent keyboard shortcuts, and a powerful API. Good for power users who want speed and efficiency.

Both demos let you test the services before deciding which one to self-host. Both work with SmartRSS.

## Step 1: Get your VPS ready

### Choosing and purchasing a VPS

RSS hosting doesn't need much. What I recommend:

- Minimum: 1GB RAM, 1 CPU core, 20GB storage
- Comfortable: 2GB RAM, 1 CPU core, 40GB storage
- Cost: $5-10/month

Easy providers for beginners:
- DigitalOcean: most beginner-friendly, good tutorials
- Linode: excellent performance, good support
- Vultr: simple interface, reliable service

### Deploy your server

1. Create an account at your chosen provider
2. Click "Create Droplet/Server"
3. Choose **Ubuntu 22.04 LTS** 
4. Pick the $5-10/month plan
5. Click "Create" and wait 2-3 minutes
6. You'll get an email with your server IP and password!

## Step 2: Connect to your server

Open your terminal (or PowerShell on Windows) and connect:

```bash
ssh root@your_server_ip
```

The first time, you'll be asked "Are you sure you want to continue connecting?" Type `yes` and press Enter.

Then paste the password from your VPS provider's email. It won't show on screen as you type, that's normal.

## Step 3: Install Docker

Just copy and paste this single command:

```bash
curl -fsSL https://get.docker.com | sh
```

This installs Docker and everything it needs. Grab a coffee, it takes 2-3 minutes.

### Test the installation

```bash
docker run hello-world
```

If you see "Hello from Docker!", you're ready.

## Step 4: Choose your RSS services

You'll pick one main reader. RSSHub and RSS-Bridge are optional extras for generating feeds from sites that don't have their own:

### The main RSS reader (pick one)

You need one main RSS reader to manage your feeds:

#### FreshRSS: the beginner-friendly choice

FreshRSS suits first-time self-hosters, or anyone who wants a traditional, familiar interface and simplicity over advanced features.

- Clean, intuitive web interface
- Easy mobile app integration
- Good API support for SmartRSS
- Simple setup and maintenance
- Large community and documentation

It uses about 100MB of RAM.

#### Miniflux: the power user's choice

Miniflux suits experienced users who want maximum speed, keyboard shortcuts, minimal distraction-free reading, and a modern tech stack.

- Very fast
- Excellent keyboard navigation
- Powerful filtering and search
- Modern, responsive design
- Built-in feed fetching optimization

It uses about 150MB of RAM including PostgreSQL.

Can't decide? Start with FreshRSS. It's easier for beginners, and you can switch later.

### Optional: RSSHub

Many modern websites (YouTube, Twitter, Instagram, Telegram, etc.) don't provide RSS feeds anymore. RSSHub generates feeds for them.

Why you might want it:

1. Feeds from 400+ platforms
2. Social media feeds: YouTube channels, Twitter users, Instagram posts
3. Custom feeds from specific websites, filters, or keywords
4. Control over feed content, update frequency, and format
5. Free and open, no API keys needed

Some examples:
- Get RSS feeds from your favorite YouTube channels
- Follow Twitter users without using Twitter
- Track Instagram posts from specific accounts
- Monitor Telegram channels
- Create feeds from websites that don't have RSS
- And hundreds more

It uses about 200MB of RAM with Redis.

My recommendation: start without RSSHub. Add it later if you need feeds from social media or non-RSS sites.

### Optional: RSS-Bridge

RSS-Bridge does the same job as RSSHub: it generates RSS and Atom feeds for websites that don't provide their own. It runs as a single PHP container, no database or cache needed. You control which bridges are enabled with a whitelist file.

My recommendation: same as RSSHub. Install it only if you need feeds from sites without RSS.

## Step 5: Set up your service

### Create the project directory

```bash
mkdir -p ~/rss-services
cd ~/rss-services
```

### Option A: FreshRSS (recommended for beginners)

```bash
mkdir freshrss && cd freshrss
nano docker-compose.yml
```

```yaml
version: "3.8"

services:
  freshrss:
    image: freshrss/freshrss:latest
    container_name: freshrss
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./freshrss-data:/var/www/FreshRSS/data
      - ./freshrss-extensions:/var/www/FreshRSS/extensions
    environment:
      - CRON_MIN=*/10
      - TZ=Asia/Shanghai
```

Change `TZ` to your timezone. Save and exit with `Ctrl+X`, then `Y`, then `Enter`.

### Option B: Miniflux (for power users)

```bash
cd ~/rss-services
mkdir miniflux && cd miniflux
nano docker-compose.yml
```

Copy and paste this configuration:

```yaml
version: "3.8"

services:
  miniflux:
    image: miniflux/miniflux:latest
    container_name: miniflux
    restart: unless-stopped
    ports:
      - "8081:8080"
    environment:
      - DATABASE_URL=postgres://miniflux:secret@miniflux-db/miniflux?sslmode=disable
      - RUN_MIGRATIONS=1
      - CREATE_ADMIN=1
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=changeme
      - BASE_URL=http://your_server_ip:8081
      - CLEANUP_FREQUENCY=24
      - POLLING_FREQUENCY=60
      - TZ=Asia/Shanghai
    depends_on:
      - miniflux-db

  miniflux-db:
    image: postgres:15
    container_name: miniflux-db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=miniflux
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=miniflux
    volumes:
      - miniflux-db:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U miniflux"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  miniflux-db:
```

Change these to your own values:
- `ADMIN_USERNAME`: your username
- `ADMIN_PASSWORD`: a strong password
- `BASE_URL`: your server IP
- `TZ`: your timezone

Save and exit with `Ctrl+X`, then `Y`, then `Enter`.

### Option C: RSSHub (optional)

Only install RSSHub if you need feeds from social media or non-RSS sites.

```bash
cd ~/rss-services
mkdir rsshub && cd rsshub
nano docker-compose.yml
```

Copy and paste this configuration:

```yaml
version: "3.8"

services:
  rsshub:
    image: diygod/rsshub:latest
    container_name: rsshub
    restart: unless-stopped
    ports:
      - "1200:1200"
    environment:
      NODE_ENV: production
      CACHE_TYPE: redis
      REDIS_URL: redis://rsshub-redis:6379/
    depends_on:
      - rsshub-redis

  rsshub-redis:
    image: redis:alpine
    container_name: rsshub-redis
    restart: unless-stopped
    volumes:
      - rsshub-redis-data:/data
    command: redis-server --appendonly yes

volumes:
  rsshub-redis-data:
```

Save and exit with `Ctrl+X`, then `Y`, then `Enter`.

### Option D: RSS-Bridge (optional)

RSS-Bridge turns websites without RSS into feeds, same idea as RSSHub. Install it only if you need that.

```bash
cd ~/rss-services
mkdir rss-bridge && cd rss-bridge
nano docker-compose.yml
```

Copy and paste this configuration:

```yaml
services:
  rss-bridge:
    image: rssbridge/rss-bridge:latest
    container_name: rss-bridge
    restart: unless-stopped
    ports:
      - "3000:80"
    volumes:
      - ./whitelist.txt:/app/whitelist.txt:ro
    environment:
      - RSSBRIDGE_whitelist_file=/app/whitelist.txt
```

Save and exit with `Ctrl+X`, then `Y`, then `Enter`.

Next, create the whitelist file. It decides which bridges are enabled. `*` enables all of them:

```bash
echo '*' > whitelist.txt
cat whitelist.txt
# *
```

If you want to limit the bridges, put bridge names in this file instead, one per line.

## Step 6: Launch your services

Navigate to your chosen service directory and start it:

### For FreshRSS:

```bash
cd ~/rss-services/freshrss
docker compose up -d
```

### For Miniflux:

```bash
cd ~/rss-services/miniflux
docker compose up -d
```

### For RSSHub (if installed):

```bash
cd ~/rss-services/rsshub
docker compose up -d
```

### For RSS-Bridge (if installed):

```bash
cd ~/rss-services/rss-bridge
docker compose up -d
```

This will download and start your services. Wait 2-3 minutes for everything to initialize.

### Check if everything is running

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose ps

# For Miniflux
cd ~/rss-services/miniflux && docker compose ps

# For RSSHub
cd ~/rss-services/rsshub && docker compose ps

# For RSS-Bridge
cd ~/rss-services/rss-bridge && docker compose ps
```

If a service shows "Up", it's working.

## Step 7: Access and configure your services

### FreshRSS setup
- URL: `http://your_server_ip:8080`
- First time: click "Installation" and create your admin account
- Good for: beginners who want a simple, clean interface

### Miniflux setup
- URL: `http://your_server_ip:8081`
- Login: use the username and password you set in the config file
- Good for: users who want speed and powerful features

### RSSHub (no setup needed)
- URL: `http://your_server_ip:1200`
- No login required, it just works
- Use it to generate RSS feeds from YouTube, Twitter, Instagram, etc.
- Documentation: open the URL to see all available routes and examples

### RSS-Bridge (no setup needed)
- URL: `http://your_server_ip:3000`
- No login required
- Use it to generate feeds for sites without RSS
- Open the URL to browse the available bridges

## Step 8: Enable API access for SmartRSS

Now connect your RSS services to SmartRSS.

### Enable FreshRSS API

1. Log in to FreshRSS at `http://your_server_ip:8080`.
2. Click your username (top right), then Administration.
3. Go to Authentication and enable API access.
4. Save the changes.
5. Generate API credentials:
   - Still in Administration, open Profile
   - Scroll to the API section
   - Click Generate to create your API password
   - Copy your API username and password. SmartRSS will need them.

### Enable Miniflux API

1. Log in to Miniflux at `http://your_server_ip:8081`.
2. Open Settings, then Integrations.
3. Enable the Google Reader API and set a username and password. These are separate from your Miniflux account login.
4. Server URL: `http://your_server_ip:8081/`


## Step 9: Connect SmartRSS to your server

Now connect SmartRSS to your self-hosted services.

### For FreshRSS users:

1. Open SmartRSS on your device.
2. Add a new account and select FreshRSS.
3. Enter your server details:
   - Server URL: `http://your_server_ip:8080/api/`
   - Username: your FreshRSS username
   - Password: your API password (from step 8)
4. Test the connection. Your feeds now sync.

### For Miniflux users:

1. Open SmartRSS on your device.
2. Add a new account and select Miniflux.
3. Enter your server details:
   - Server URL: `http://your_server_ip:8081/`
   - Username: your Miniflux Google Reader username
   - Password: your Miniflux Google Reader password
4. Test the connection, and you're done.

### Add feeds from RSSHub

Want to follow a YouTube channel or Twitter user that doesn't have RSS?

1. Open RSSHub at `http://your_server_ip:1200`.
2. Find the route you need, for example `/youtube/user/:username`.
3. Copy the RSS feed URL.
4. Add it in SmartRSS, or in your FreshRSS or Miniflux web interface.

Popular RSSHub routes:
- YouTube: `http://your_server_ip:1200/youtube/user/:username`
- Twitter: `http://your_server_ip:1200/twitter/user/:username`
- Instagram: `http://your_server_ip:1200/instagram/user/:username`
- Telegram: `http://your_server_ip:1200/telegram/channel/:channelname`

### Add feeds from RSS-Bridge

1. Open RSS-Bridge at `http://your_server_ip:3000`.
2. Pick a bridge from the list and fill in the fields it asks for.
3. Copy the RSS or Atom URL it generates.
4. Add that URL in SmartRSS, or in your FreshRSS or Miniflux web interface.

## Quick management commands

### Check service status

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose ps

# For Miniflux
cd ~/rss-services/miniflux && docker compose ps

# For RSSHub
cd ~/rss-services/rsshub && docker compose ps

# For RSS-Bridge
cd ~/rss-services/rss-bridge && docker compose ps
```

### View logs (if something goes wrong)

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose logs -f

# For Miniflux
cd ~/rss-services/miniflux && docker compose logs -f

# For RSSHub
cd ~/rss-services/rsshub && docker compose logs -f

# For RSS-Bridge
cd ~/rss-services/rss-bridge && docker compose logs -f
```

### Restart a service

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose restart

# For Miniflux
cd ~/rss-services/miniflux && docker compose restart

# For RSSHub
cd ~/rss-services/rsshub && docker compose restart

# For RSS-Bridge
cd ~/rss-services/rss-bridge && docker compose restart
```

### Update your services

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose pull && docker compose up -d

# For Miniflux
cd ~/rss-services/miniflux && docker compose pull && docker compose up -d

# For RSSHub
cd ~/rss-services/rsshub && docker compose pull && docker compose up -d

# For RSS-Bridge
cd ~/rss-services/rss-bridge && docker compose pull && docker compose up -d
```

### Stop services

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose down

# For Miniflux
cd ~/rss-services/miniflux && docker compose down

# For RSSHub
cd ~/rss-services/rsshub && docker compose down

# For RSS-Bridge
cd ~/rss-services/rss-bridge && docker compose down
```

## Common issues and fixes

### Services won't start

```bash
# Check what's wrong (replace with your service)
cd ~/rss-services/freshrss  # or miniflux, rsshub, or rss-bridge
docker compose logs

# Restart everything
docker compose restart
```

### Can't access your server

Make sure your VPS provider's firewall allows these ports (only for services you installed):
- 8080 (FreshRSS)
- 8081 (Miniflux)
- 1200 (RSSHub)
- 3000 (RSS-Bridge)

### SmartRSS won't connect

1. Double-check your server URL, including `http://` and the port number.
2. Verify your API credentials. Regenerate them if needed.
3. Test the web interface in your browser first. If you can log in there, the server itself is fine.

## Conclusion

You now have your own RSS backend that syncs with SmartRSS across all your devices. Your reading stays on your own server, and there are no monthly fees.

Start adding your favorite feeds.

Need help? Check the official documentation:
- [FreshRSS Documentation](https://freshrss.github.io/FreshRSS/)
- [Miniflux Documentation](https://miniflux.app/docs/)
- [RSSHub Documentation](https://docs.rsshub.app/)
- [RSS-Bridge Documentation](https://rss-bridge.github.io/rss-bridge/index.html)

Happy reading!

---

*Download SmartRSS and connect it to your new backend.*

<div class="app-download-section">
  <h3>📱 Download SmartRSS Now</h3>
  <p>Available on iOS, Android, and Windows platforms</p>
  <div class="download-buttons">
    <a href="https://apps.apple.com/app/smartrss-ai-rss-reader/id6749771900" class="download-btn">
      <span class="btn-icon">🍎</span>
      Download for iOS
    </a>
    <a href="https://play.google.com/store/apps/details?id=com.vinsonguo.flutter_rss_reader" class="download-btn">
      <span class="btn-icon">🤖</span>
      Download for Android
    </a>
    <a href="https://github.com/VinsonGuo/SmartRSS-Windows/releases" class="download-btn">
      <span class="btn-icon">💻</span>
      Download for Windows
    </a>
  </div>
</div>