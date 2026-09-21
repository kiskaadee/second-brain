---
type: knowledge
status: stable
topics: ['aria2c', 'cli', 'networking', 'bittorrent']
---

# aria2c Quickstart Guide

`aria2c` is a lightweight, multi-protocol, multi-source command-line download utility supporting BitTorrent, HTTP/HTTPS, FTP, and Metalink.

---

## 1. BitTorrent & Magnet Links

### Download from a Magnet Link
Always wrap magnet links in quotes to avoid shell escaping issues with `&` and `?`:
```bash
aria2c "magnet:?xt=urn:btih:EXAMPLE_HASH&dn=Example+Name"
```

### Download from a `.torrent` File or URL
```bash
# Local torrent file
aria2c /path/to/linux.torrent

# Remote torrent URL
aria2c "https://releases.ubuntu.com/24.04/ubuntu-24.04-desktop-amd64.iso.torrent"
```

### Specify Output Directory
```bash
aria2c -d ~/Downloads "magnet:?xt=urn:btih:..."
```

---

## 2. Torrent Management & Seeding Options

### Control Seeding
By default, aria2 continues seeding after downloading completes.
```bash
# Do not seed after download completes
aria2c --seed-time=0 "magnet:?xt=urn:btih:..."

# Seed until reaching a 1.5 ratio or 30 minutes
aria2c --seed-ratio=1.5 --seed-time=30 "magnet:?xt=urn:btih:..."
```

### Rate Limiting (Bandwidth)
```bash
# Limit download speed to 5 MB/s and upload speed to 500 KB/s
aria2c --max-download-limit=5M --max-upload-limit=500K "magnet:?xt=urn:btih:..."
```

### Selective File Downloading (Multi-File Torrents)
1. **List all files in the torrent:**
   ```bash
   aria2c -S /path/to/file.torrent
   ```
2. **Download only specific file indices:**
   ```bash
   aria2c --select-file=1,3-5 /path/to/file.torrent
   ```

---

## 3. High-Speed Direct Downloads (HTTP/HTTPS/FTP)

Accelerate regular downloads by splitting into multiple connections and sources:
```bash
# -x: Max connections per server (up to 16)
# -s: Split file into N parts
# -k: Minimum split size
aria2c -x 16 -s 16 -k 1M "https://example.com/large-archive.tar.gz"
```

---

## 4. Useful Batch & Session Commands

### Download from a URL/Magnet List File
```bash
# Read URLs or magnet links from a text file (one per line)
aria2c -i downloads.txt
```

### Save Session for Resuming Later
```bash
aria2c --save-session=session.txt --save-session-interval=60 -i downloads.txt

# Resume from saved session
aria2c -i session.txt
```
