# Printer Discovery & Setup Guide (`avahi-browse` & `lpinfo`)

This guide covers the architecture, tooling, options, and step-by-step procedures for discovering, diagnosing, and configuring printers on Linux, with specific focus on **CUPS**, **mDNS/Zeroconf**, and **NixOS**.

---

## 1. Architectural Overview: The Linux Printing Stack

When an application prints a document, it interacts with several layered subsystems:

```text
[ Application ] (Browser, LibreOffice, Document Viewer)
       │
       ▼
[ GTK / Qt Print Dialog ] (Discovers IPP printers on-demand via Avahi/mDNS)
       │
       ▼
[ CUPS Daemon ] (Scheduler: queues, job management, routing)
   ├── Configuration: /etc/cups/printers.conf
   ├── Spooler: /var/spool/cups/
   └── Filters: Converts PDF/PostScript -> Raster format (PWG Raster, Apple Raster)
       │
       ▼
[ CUPS Backends ] (Communication channel: usb, ipp, ipps, socket, dnssd)
       │
       ▼
[ Physical Printer ] (USB or LAN Wi-Fi / Ethernet)
```

### Discovery Paradigms: mDNS vs. CUPS Backends

Finding a printer on Linux is handled by two distinct toolchains operating at different layers:

| Layer | Primary Tool | Mechanism | Scope |
| :--- | :--- | :--- | :--- |
| **Network Service Discovery (mDNS / DNS-SD)** | `avahi-browse` | Multicast DNS over UDP `5353`. Interrogates the local broadcast domain for advertised services (`_ipp._tcp`, `_printer._tcp`). | Network printers only (Wi-Fi / Ethernet). Independent of CUPS. |
| **CUPS Device & Driver Query** | `lpinfo` | Direct CUPS subsystem probe. Scans local hardware busses (USB, parallel) and network backends (`socket://`, `ipp://`, `snmp`). | USB printers, network backends, and installed printer driver PPDs. |
| **IPP Service Probe** | `ippfind` / `ipptool` | CUPS-native tool querying IPP endpoints directly over HTTP/HTTPS. | Modern network printers supporting IPP / IPP Everywhere. |

---

## 2. Deep Dive: `avahi-browse`

### Role & Purpose
`avahi-browse` is the CLI client for **Avahi**, the Linux implementation of Multicast DNS (mDNS) and DNS Service Discovery (DNS-SD) (often called Zeroconf or Bonjour). 

When a modern printer powers on, its embedded network stack announces its presence to the local network by broadcasting DNS records on `224.0.0.251:5353` (IPv4) or `[FF02::FB]:5353` (IPv6). `avahi-browse` listens for and queries these records.

### Key CLI Flags & Options

| Option | Long Flag | Description | Why It Matters |
| :--- | :--- | :--- | :--- |
| `-r` | `--resolve` | **Crucial:** Resolves service names to hostnames, IP addresses, port numbers, and TXT records. | Without `-r`, you only get friendly names (e.g. `"EPSON ET-3850"`). With `-r`, you get the exact resource path (`rp=ipp/print`) and IP needed to construct the URI. |
| `-t` | `--terminate` | Exits after dumping current cache and initial query response. | By default, `avahi-browse` runs indefinitely waiting for events. `-t` is necessary for one-shot terminal checks or scripts. |
| `-a` | `--all` | Browses for all service types registered on the LAN. | Useful for general network reconnaissance when you do not know what service the printer advertises. |
| `-p` | `--parsable` | Formats output as semicolon-delimited text. | Essential for shell scripting and automation. |
| `-d` | `--domain` | Specifies domain to browse (default: `local`). | Rarely changed unless using custom unicast DNS-SD domains. |
| `-c` | `--cache` | Only looks at the local Avahi cache (does not send network queries). | Fast, but may miss newly connected devices. |

### Relevant Service Types for Printing & Scanning

Instead of browsing all traffic, target specific service types:
- `_ipp._tcp`: Standard Internet Printing Protocol (port 631). **Primary target for modern printers.**
- `_ipps._tcp`: Secure IPP over TLS.
- `_printer._tcp`: Legacy LPD/LPR line printer daemon (port 515).
- `_pdl-datastream._tcp`: Raw socket printing / AppSocket / HP JetDirect (port 9100).
- `_uscan._tcp` / `_scanner._tcp`: Network scanning (eSCL / AirScan / WSD).

### Command Recipes

#### 1. Discover all IPP printers with full connection details
```bash
avahi-browse -rt _ipp._tcp
```

#### 2. Discover both printing and scanning services
```bash
avahi-browse -rt _ipp._tcp _ipps._tcp _uscan._tcp
```

#### 3. Parsable one-liner to extract host, port, and TXT records
```bash
avahi-browse -rtp _ipp._tcp
```

### Interpreting `avahi-browse` Output

A resolved record looks like this:

```text
+ wlp1s0 IPv4 EPSON ET-3850 Series                  _ipp._tcp            local
= wlp1s0 IPv4 EPSON ET-3850 Series                  _ipp._tcp            local
   hostname = [EPSON123456.local]
   address = [192.168.1.150]
   port = [631]
   txt = [
     "txtvers=1"
     "qtotal=1"
     "rp=ipp/print"
     "ty=EPSON ET-3850 Series"
     "adminurl=http://EPSON123456.local.:631/PRESENTATION/BONJOUR"
     "pdl=application/octet-stream,image/pwg-raster,image/urf"
     "Duplex=T"
     "Color=T"
   ]
```

#### Decoded Fields:
- **`hostname`**: `EPSON123456.local` — The mDNS address.
- **`address`**: `192.168.1.150` — Current IP assigned via DHCP.
- **`port`**: `631` — Standard IPP port.
- **`rp` (Resource Path)**: `ipp/print` — The path on the printer's web server where IPP requests must be POSTed.
- **`ty` (Type/Model)**: Human-readable model string.
- **`pdl` (Page Description Languages)**: Formats the printer accepts natively. If `image/pwg-raster` or `image/urf` are listed, the printer supports **driverless printing** (IPP Everywhere / AirPrint).
- **`Duplex=T`**: Confirms hardware automatic two-sided printing is supported.

#### Constructing the Device URI:
Combine `address` (or `hostname`), `port`, and `rp`:
```text
ipp://192.168.1.150:631/ipp/print
# or using mDNS hostname:
ipp://EPSON123456.local:631/ipp/print
```

---

## 3. Deep Dive: `lpinfo`

### Role & Purpose
`lpinfo` is a CUPS administrative utility. Rather than scanning raw network packets like Avahi, `lpinfo` queries **CUPS backend executables** (stored in `/usr/lib/cups/backend/` or Nix store equivalents) to report:
1. Available physical and networked printer devices (`-v`).
2. Installed printer drivers and PPD (PostScript Printer Description) files (`-m`).

### Key CLI Flags & Options

| Option | Long Flag | Description | Why It Matters |
| :--- | :--- | :--- | :--- |
| `-v` | N/A | **List Devices**: Queries all installed CUPS backends for connected printers. | Reveals exact URI formats expected by CUPS (`usb://`, `socket://`, `dnssd://`). |
| `-m` | N/A | **List Drivers / Models**: Lists all PPD files available to CUPS. | Needed to find the exact model string for legacy or proprietary drivers (e.g. `epson-escpr`). |
| `-l` | N/A | **Long Listing**: Shows extended metadata for devices or drivers. | Displays IEEE-1284 device IDs, languages, and make/model strings. |
| `--make-and-model` | N/A | Filters model listing by manufacturer/model regex. | Avoids scrolling through thousands of PPDs when searching for a specific printer. |
| `--timeout` | N/A | Timeout in seconds for device scanning. | Prevents network backend probes (like SNMP) from blocking for too long. |

### Command Recipes

#### 1. Scan for connected devices (USB and detected network printers)
```bash
lpinfo -v
```

Output format:
```text
direct usb://EPSON/ET-3850%20Series?serial=58344...
network ipp://192.168.1.150:631/ipp/print
network socket://192.168.1.150:9100
network dnssd://EPSON%20ET-3850._ipp._tcp.local/
```

- **`direct`**: Physical hardware connection (USB, parallel).
- **`network`**: Network communication protocol.

#### 2. Search for Epson ESC/P-R drivers
```bash
lpinfo -m | grep -i escpr
```
Example match:
```text
epson-inkjet-printer-escpr/Epson-ET-3850_Series-epson-escpr-en.ppd Epson ET-3850 Series, Epson Inkjet Printer Driver (ESC/P-R) for Linux
```
The first column before the space is the **PPD identifier** used for CUPS configuration.

#### 3. Check for the generic driverless PPD
```bash
lpinfo -m | grep everywhere
```
Output:
```text
everywhere IPP Everywhere
```
*(The `everywhere` keyword tells CUPS to query the printer dynamically and generate a PPD on-the-fly).*

---

## 4. Complementary Tool: `ippfind`

`ippfind` is part of modern CUPS distributions. It combines mDNS discovery with IPP capability verification in a single lightweight command:

```bash
# Locate all IPP printers and print their URIs
ippfind

# Output:
# ipp://EPSON123456.local:631/ipp/print
```

You can test communication directly with `ipptool`:
```bash
ipptool -tv ipp://192.168.1.150:631/ipp/print get-printer-attributes.test
```
If this command returns printer status attributes (e.g. `printer-state=idle`), the printer is 100% functional and reachable via IPP.

---

## 5. End-to-End Setup Workflows

### Method A: Modern Driverless Setup (IPP Everywhere) — Recommended

Most network printers made after 2013 support IPP Everywhere. You do not need vendor PPDs or custom drivers.

1. **Discover URI**:
   ```bash
   ippfind
   # Returns: ipp://EPSON123456.local:631/ipp/print
   ```

2. **Add Queue Imperatively (CUPS CLI)**:
   ```bash
   lpadmin -p "Epson_Home" -E -v "ipp://EPSON123456.local:631/ipp/print" -m everywhere
   lpadmin -d "Epson_Home"  # Set as default
   ```
   *Explanation of flags:*
   - `-p <name>`: Queue name (no spaces).
   - `-E`: Enables the printer and tells CUPS to accept incoming print jobs immediately.
   - `-v <uri>`: The device URI discovered.
   - `-m everywhere`: Instructs CUPS to query printer attributes and autogenerate the driver.

3. **Or Add Declaratively in NixOS**:
   ```nix
   hardware.printers = {
     ensurePrinters = [
       {
         name = "Epson_Home";
         location = "Home Office";
         deviceUri = "ipp://EPSON123456.local:631/ipp/print";
         model = "everywhere";
         ppdOptions = {
           PageSize = "Letter";
           Duplex = "DuplexNoTumble";
         };
       }
     ];
     ensureDefaultPrinter = "Epson_Home";
   };
   ```

---

### Method B: Vendor Driver Setup (e.g., Epson ESC/P-R)

Use this method for USB printers or older models lacking IPP Everywhere.

1. **Find Device URI**:
   ```bash
   lpinfo -v | grep -i epson
   # Example output: direct usb://EPSON/ET-3850?serial=123456789
   ```

2. **Find Model PPD**:
   ```bash
   lpinfo -m | grep -i "ET-3850"
   # Output: epson-inkjet-printer-escpr/Epson-ET-3850_Series-epson-escpr-en.ppd
   ```

3. **Add Queue Imperatively**:
   ```bash
   lpadmin -p "Epson_USB" -E \
     -v "usb://EPSON/ET-3850?serial=123456789" \
     -m "epson-inkjet-printer-escpr/Epson-ET-3850_Series-epson-escpr-en.ppd"
   ```

4. **Or Add Declaratively in NixOS**:
   ```nix
   hardware.printers = {
     ensurePrinters = [
       {
         name = "Epson_USB";
         location = "Desk";
         deviceUri = "usb://EPSON/ET-3850?serial=123456789";
         model = "epson-inkjet-printer-escpr/Epson-ET-3850_Series-epson-escpr-en.ppd";
       }
     ];
   };
   ```

---

## 6. Network Scanner Discovery (SANE / eSCL)

Many multifunction Epson devices feature both printing and scanning.

1. **Check mDNS Scanner Advertisement**:
   ```bash
   avahi-browse -rt _uscan._tcp
   ```
   If present, the scanner supports **eSCL / AirScan** (driverless scanning).

2. **List Available Scanners with SANE**:
   ```bash
   scanimage -L
   ```
   Expected output for driverless eSCL:
   ```text
   device `airscan:e0:EPSON ET-3850' is a eSCL EPSON ET-3850 ip=192.168.1.150
   ```

3. **Perform a Test Scan**:
   ```bash
   scanimage -d "airscan:e0:EPSON ET-3850" --format=png --output-file test.png
   ```

---

## 7. Troubleshooting Matrix

| Symptom | Probable Cause | Diagnostic Command & Fix |
| :--- | :--- | :--- |
| `avahi-browse` produces no output for printer | Printer in sleep mode or on another subnet/guest Wi-Fi | Wake printer via power button. Check router client list. Ensure host and printer are on the same VLAN without AP client isolation. |
| `avahi-browse` returns records, but `.local` fails to resolve | Avahi NSS name resolution module disabled | Check `/etc/nsswitch.conf` for `hosts: ... mdns4_minimal [NOTFOUND=return] dns`. In NixOS, set `services.avahi.nssmdns4 = true`. |
| Printer prints endless blank pages or raw PostScript code | Driver mismatch / raw queue sending raster to PostScript or vice-versa | Switch queue model to `everywhere` or exact `epson-escpr` PPD. Avoid generic PCL drivers for Epson inkjet hardware. |
| Print jobs immediately pause with "Unable to locate printer" | Hardcoded DHCP IP changed | Re-discover with `avahi-browse -rt _ipp._tcp` and update the URI with a DHCP static reservation or `.local` mDNS hostname. |
| Queue is stopped / rejected | Job error caused CUPS to halt the queue | Check queue status with `lpstat -p -d`. Resume queue with `cupsenable <queue>` and `cupsaccept <queue>`. Clear stuck jobs with `cancel -a`. |

---

## 8. Summary Comparison

```text
Discovery Task                    Preferred Tool            Command
──────────────────────────────────────────────────────────────────────────────────────────
Quick network printer find        ippfind                   ippfind
Detailed network mDNS records     avahi-browse              avahi-browse -rt _ipp._tcp
USB / Hardware backend probe      lpinfo                    lpinfo -v
Available PPD driver list         lpinfo                    lpinfo -m | grep <model>
Verify printer IPP responses      ipptool                   ipptool -tv <uri> get-printer-attributes.test
List active queues & defaults     lpstat                    lpstat -p -d
Create or modify queue            lpadmin                   lpadmin -p <name> -E -v <uri> -m <model>
```
