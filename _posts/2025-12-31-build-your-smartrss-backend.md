---
layout: post
title: "Build Your RSS Backend for SmartRSS: A Beginner's Guide to FreshRSS, Miniflux, and RSSHub"
author: "Vinson Guo"
categories: [tutorial, self-hosting, rss, docker, smartrss]
---

Want to supercharge your **SmartRSS** experience with a powerful, self-hosted backend? This guide will show you how to set up **FreshRSS**, **Miniflux**, and **RSSHub** - even if you've never touched a server before! These services will sync seamlessly with SmartRSS, giving you complete control over your RSS reading experience.

## Why Build Your Own RSS Backend?

Setting up your own RSS server gives you amazing benefits:

- **Perfect SmartRSS Integration**: Sync your feeds across all devices
- **Complete Privacy**: Your reading habits stay on your own server
- **No Monthly Fees**: Pay once for a VPS, run forever
- **Unlimited Feeds**: No restrictions on the number of subscriptions
- **Super Fast**: Your own dedicated RSS infrastructure

## What You'll Need

- A VPS (Virtual Private Server) - $5-10/month
- About 30 minutes of your time
- No coding experience required!

## Quick Start: Try Official Instances First

Before setting up your own server, you can try these official demo instances:

### Official FreshRSS Demo
- **URL**: `https://demo.freshrss.org/`
- **Features**: Clean interface, mobile-friendly, great API support
- **Perfect for**: Beginners who want a traditional RSS experience

### Official Miniflux Demo  
- **URL**: `https://miniflux.app/` (offers free trial)
- **Features**: Modern design, excellent keyboard shortcuts, powerful API
- **Perfect for**: Power users who want speed and efficiency

These demos let you test both services before deciding which one to self-host. Both work perfectly with SmartRSS!

## Step 1: Get Your VPS Ready

### Choosing and Purchasing a VPS

For RSS hosting, you don't need anything powerful. Here's what I recommend:

- **Minimum specs**: 1GB RAM, 1 CPU core, 20GB storage
- **Perfect choice**: 2GB RAM, 1 CPU core, 40GB storage
- **Cost**: $5-10/month

**Easy VPS providers for beginners:**
- **DigitalOcean** - Most beginner-friendly, great tutorials
- **Linode** - Excellent performance, good support  
- **Vultr** - Simple interface, reliable service

### Deploy Your Server (Super Simple!)

1. Create an account at your chosen provider
2. Click "Create Droplet/Server"
3. Choose **Ubuntu 22.04 LTS** 
4. Pick the $5-10/month plan
5. Click "Create" and wait 2-3 minutes
6. You'll get an email with your server IP and password!

## Step 2: Connect to Your Server

Open your terminal (or PowerShell on Windows) and connect:

```bash
ssh root@your_server_ip
```

**First time?** You'll see a message asking "Are you sure you want to continue connecting?" Type `yes` and press Enter.

**Password?** Paste the password from your VPS provider's email (you won't see it appear on screen - that's normal!).

## Step 3: Install Docker (One Command!)

Just copy and paste this single command:

```bash
curl -fsSL https://get.docker.com | sh
```

This will automatically install Docker and everything you need. Grab a coffee - it takes 2-3 minutes!

### Test Docker Installation

```bash
docker run hello-world
```

If you see "Hello from Docker!" - you're ready to go! 

## Step 4: Choose Your RSS Services

Before setting up, let's understand your options. We have a **2+1 architecture**:

### The Main RSS Reader (Choose One)

You need **one** main RSS reader to manage your feeds:

#### FreshRSS - The Beginner-Friendly Choice 

**Perfect for:**
- First-time self-hosters
- Users who want a traditional, familiar interface
- Those who prefer simplicity over advanced features

**Why Choose FreshRSS:**
- Clean, intuitive web interface
- Easy mobile app integration
- Great API support for SmartRSS
- Simple setup and maintenance
- Large community and documentation

**Resource Usage:** Light (~100MB RAM)

#### Miniflux - The Power User's Choice 

**Perfect for:**
- Experienced users who want maximum speed
- Keyboard shortcut enthusiasts
- Users who prefer minimal, distraction-free reading
- Those who want the most modern tech stack

**Why Choose Miniflux:**
- Blazing fast performance
- Excellent keyboard navigation
- Powerful filtering and search
- Modern, responsive design
- Built-in feed fetching optimization

**Resource Usage:** Light (~150MB RAM including PostgreSQL)

**Can't Decide?** Start with **FreshRSS** - it's easier for beginners, and you can always switch later!

### Optional: RSSHub - The RSS Supercharger 

**What is RSSHub?**

RSSHub is a game-changer for RSS users. Many modern websites (YouTube, Twitter, Instagram, Telegram, etc.) don't provide RSS feeds anymore. RSSHub solves this by generating RSS feeds from virtually any website!

**Why You Might Want RSSHub:**

1. **No RSS? No Problem!** - Generate feeds from 400+ platforms
2. **Social Media Feeds** - YouTube channels, Twitter users, Instagram posts
3. **Custom Content** - Create feeds from specific websites, filters, or keywords
4. **Flexible & Powerful** - Customize feed content, update frequency, and format
5. **Free & Open** - No API keys needed, community-driven

**Examples of what RSSHub can do:**
- Get RSS feeds from your favorite YouTube channels
- Follow Twitter users without using Twitter
- Track Instagram posts from specific accounts
- Monitor Telegram channels
- Create feeds from websites that don't have RSS
- And hundreds more use cases!

**Resource Usage:** Moderate (~200MB RAM with Redis)

**Recommendation:** Start without RSSHub. Add it later if you need feeds from social media or non-RSS websites.

## Step 5: Set Up Your Chosen Service

### Create Project Directory

```bash
mkdir -p ~/rss-services
cd ~/rss-services
```

### Option A: FreshRSS Setup (Recommended for Beginners)

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

**Configuration:**
- `TZ=Asia/Shanghai` → Change to your timezone

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

### Option B: Miniflux Setup (For Power Users)

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

**Configuration:**
- `ADMIN_USERNAME=admin` → Your desired username
- `ADMIN_PASSWORD=changeme` → Choose a strong password
- `BASE_URL=http://your_server_ip:8081` → Replace with your server IP
- `TZ=Asia/Shanghai` → Change to your timezone

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

### Option C: Add RSSHub (Optional)

**Only install RSSHub if you need feeds from social media or non-RSS websites.**

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

**Save and exit**: Press `Ctrl+X`, then `Y`, then `Enter`

## Step 6: Launch Your Services

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

This will download and start your services. Wait 2-3 minutes for everything to initialize.

### Check if Everything is Running

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose ps

# For Miniflux
cd ~/rss-services/miniflux && docker compose ps

# For RSSHub
cd ~/rss-services/rsshub && docker compose ps
```

You should see services marked as "Up" - that means they're working!

## Step 7: Access and Configure Your Services

### FreshRSS Setup
- **URL**: `http://your_server_ip:8080`
- **First time**: Click "Installation" and create your admin account
- **Perfect for**: Beginners who want a simple, clean interface

### Miniflux Setup
- **URL**: `http://your_server_ip:8081`
- **Login**: Use the username/password you set in the config file
- **Perfect for**: Users who want speed and powerful features

### RSSHub (No Setup Needed!)
- **URL**: `http://your_server_ip:1200`
- **No login required** - it just works!
- **Use it to**: Generate RSS feeds from YouTube, Twitter, Instagram, etc.
- **Documentation**: Visit the URL to see all available routes and examples

## Step 8: Enable API Access for SmartRSS

Now the exciting part - connecting your RSS services to SmartRSS!

### Enable FreshRSS API

1. **Login to FreshRSS** at `http://your_server_ip:8080`
2. **Click on your username** (top right) → **Administration**
3. **Go to "Authentication"** → Enable **"Enable API access"**
4. **Save changes**
5. **Generate API credentials**:
   - Still in Administration, go to **"Profile"**
   - Scroll to **"API"** section
   - Click **"Generate"** to create your API password
   - **Copy your API username and password** - you'll need these for SmartRSS!

### Enable Miniflux API

Great news! **Miniflux API is enabled by default** - no setup needed!

## Step 9: Connect SmartRSS to Your Server

Now you can connect SmartRSS to your self-hosted services!

### For FreshRSS Users:

1. **Open SmartRSS** on your device
2. **Add a new account** → Select **"FreshRSS"**
3. **Enter your server details**:
   - **Server URL**: `http://your_server_ip:8080/api/`
   - **Username**: Your FreshRSS username
   - **Password**: Your API password (from Step 7)
4. **Test connection** and enjoy your synced feeds!

### For Miniflux Users:

1. **Open SmartRSS** on your device  
2. **Add a new account** → Select **"Miniflux"**
3. **Enter your server details**:
   - **Server URL**: `http://your_server_ip:8081/`
   - **Username**: Your Miniflux username
   - **Password**: Your Miniflux password
4. **Test connection** and you're ready to go!

### Add Feeds from RSSHub

Want to follow a YouTube channel or Twitter user that doesn't have RSS?

1. **Browse RSSHub** at `http://your_server_ip:1200`
2. **Find the route you need** (e.g., `/youtube/user/:username`)
3. **Copy the RSS feed URL**
4. **Add it directly in SmartRSS** or your FreshRSS/Miniflux web interface!

**Popular RSSHub routes:**
- **YouTube**: `http://your_server_ip:1200/youtube/user/:username`
- **Twitter**: `http://your_server_ip:1200/twitter/user/:username`  
- **Instagram**: `http://your_server_ip:1200/instagram/user/:username`
- **Telegram**: `http://your_server_ip:1200/telegram/channel/:channelname`

## Quick Management Commands

### Check Service Status

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose ps

# For Miniflux
cd ~/rss-services/miniflux && docker compose ps

# For RSSHub
cd ~/rss-services/rsshub && docker compose ps
```

### View Logs (if something goes wrong)

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose logs -f

# For Miniflux
cd ~/rss-services/miniflux && docker compose logs -f

# For RSSHub
cd ~/rss-services/rsshub && docker compose logs -f
```

### Restart a Service

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose restart

# For Miniflux
cd ~/rss-services/miniflux && docker compose restart

# For RSSHub
cd ~/rss-services/rsshub && docker compose restart
```

### Update Your Services

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose pull && docker compose up -d

# For Miniflux
cd ~/rss-services/miniflux && docker compose pull && docker compose up -d

# For RSSHub
cd ~/rss-services/rsshub && docker compose pull && docker compose up -d
```

### Stop Services

```bash
# For FreshRSS
cd ~/rss-services/freshrss && docker compose down

# For Miniflux
cd ~/rss-services/miniflux && docker compose down

# For RSSHub
cd ~/rss-services/rsshub && docker compose down
```

## Common Issues and Fixes

### Services Won't Start

```bash
# Check what's wrong (replace with your service)
cd ~/rss-services/freshrss  # or miniflux or rsshub
docker compose logs

# Restart everything
docker compose restart
```

### Can't Access Your Server

Make sure your VPS provider's firewall allows these ports (only for services you installed):
- **8080** (FreshRSS)
- **8081** (Miniflux)
- **1200** (RSSHub)

### SmartRSS Won't Connect

1. **Double-check your server URL** - include `http://` and the port number
2. **Verify your API credentials** - re-generate them if needed
3. **Test the web interface** - make sure you can login in your browser first

## Conclusion

You've just built your own RSS backend that works perfectly with SmartRSS! Your feeds will sync across all your devices, you have complete privacy, and you're saving money on monthly subscription fees.

Start adding your favorite feeds and enjoy the ultimate RSS experience! 

**Need help?** Check out the official documentation:
- [FreshRSS Documentation](https://freshrss.github.io/FreshRSS/)
- [Miniflux Documentation](https://miniflux.app/docs/)  
- [RSSHub Documentation](https://docs.rsshub.app/)

Happy reading! 

---

*Ready to supercharge your RSS experience? Download today and start using these powerful AI prompts!*

<div class="app-download-section">
  <h3>📱 Download SmartRSS Now</h3>
  <p>Available on both iOS and Android platforms</p>
  <div class="download-buttons">
    <a href="https://apps.apple.com/app/smartrss-ai-rss-reader/id6749771900" class="download-btn">
      <span class="btn-icon">🍎</span>
      Download for iOS
    </a>
    <a href="https://play.google.com/store/apps/details?id=com.vinsonguo.flutter_rss_reader" class="download-btn">
      <span class="btn-icon">🤖</span>
      Download for Android
    </a>
  </div>
</div>