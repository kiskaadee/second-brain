---
type: guide
status: testing
project: nixos
tags:
  - nixos
  - security
  - firewall
  - networkmanager
  - iptables
  - workstation
---

# Dynamic Trusted Wi-Fi Firewall Configuration (Testing)

> **Status**: Testing / Experimental · **Host**: `laptop` (`~/Config`) · **Subsystem**: `system/core.nix`

This guide documents the architecture, implementation, and verification procedure for a dynamic, SSID-aware firewall on mobile NixOS workstations.

---

## 1. Problem Statement & Operational Friction

Mobile workstations operating on NixOS enforce strict ingress firewall policies by default (`networking.firewall.enable = true`). While this default protects machines on public or hostile networks (cafes, airports, conferences), it introduces operational friction during local development:

* **Ad-Hoc Port Friction**: Running local development servers (Vite on `:5173`, FastAPI on `:8000`, test webhooks, or mobile preview servers) requires opening incoming ports so secondary devices (phones, tablets) on the LAN can connect.
* **Security vs. Convenience Anti-Pattern**: Opening ports globally via `networking.firewall.allowedTCPPorts = [ 8000 5173 ... ]` leaves those ports permanently open on all networks, including untrusted public Wi-Fi.
* **Manual Toggling Anti-Pattern**: Disabling the firewall manually via `sudo systemctl stop firewall` creates risk if the operator forgets to re-enable it before traveling.

---

## 2. Architecture & Design

The solution relies on an event-driven, declarative pattern combining a dedicated `iptables` sub-chain with a NetworkManager dispatcher script:

```text
                  Incoming Packet (wlo1)
                            │
                            ▼
                    [INPUT / nixos-fw]
                            │
                      (JUMP rule 1)
                            │
                            ▼
                   [nixos-fw-home]
                   /             \
    If SSID == "VICTORIA"     If Other / Down
           │                         │
     [-i wlo1 -j ACCEPT]         [FLUSH -F]
           │                         │
      (Allow All)             (Falls through to strict
                               NixOS default DROP)
```

### Key Invariants
1. **Isolated Chain**: All dynamic rules live inside a dedicated sub-chain `nixos-fw-home`. The base `nixos-fw` chain is never mutated directly by runtime scripts.
2. **Fail-Safe Fallback**: If disconnected or connected to any SSID other than `"VICTORIA"`, `nixos-fw-home` is immediately flushed (`-F`), restoring the default strict drop policy instantly.
3. **Dual Stack**: Both IPv4 (`iptables`) and IPv6 (`ip6tables`) chains are managed symmetrically.

---

## 3. Declarative NixOS Implementation

The implementation is located in `~/Config/system/core.nix`:

```nix
  # 🛡️ Dynamic Firewall for Trusted Home Wi-Fi
  # Automatically marks the Wi-Fi interface as fully trusted (accepting all incoming ports)
  # ONLY when connected to the trusted home Wi-Fi network ("VICTORIA"), removing the friction of
  # managing arbitrary development ports. Restores the strict default firewall immediately upon
  # disconnecting or connecting to any public / untrusted network.
  networking.firewall.extraCommands = ''
    iptables -N nixos-fw-home 2>/dev/null || true
    iptables -C nixos-fw -j nixos-fw-home 2>/dev/null || iptables -I nixos-fw 1 -j nixos-fw-home
    ip6tables -N nixos-fw-home 2>/dev/null || true
    ip6tables -C nixos-fw -j nixos-fw-home 2>/dev/null || ip6tables -I nixos-fw 1 -j nixos-fw-home
  '';

  networking.networkmanager.dispatcherScripts = [
    {
      source = pkgs.writeShellScript "nm-trusted-wifi-firewall" ''
        IFACE="$1"
        ACTION="$2"
        TRUSTED_SSID="VICTORIA"

        IPT="${pkgs.iptables}/bin/iptables"
        IP6T="${pkgs.iptables}/bin/ip6tables"
        LOGGER="${pkgs.util-linux}/bin/logger"

        manage_chain() {
          local cmd="$1"
          $cmd -N nixos-fw-home 2>/dev/null || true
          $cmd -C nixos-fw -j nixos-fw-home 2>/dev/null || $cmd -I nixos-fw 1 -j nixos-fw-home
        }

        manage_chain "$IPT"
        manage_chain "$IP6T"

        if [ "$ACTION" = "up" ] && [ "$CONNECTION_ID" = "$TRUSTED_SSID" ]; then
          $IPT -F nixos-fw-home
          $IPT -A nixos-fw-home -i "$IFACE" -j ACCEPT

          $IP6T -F nixos-fw-home
          $IP6T -A nixos-fw-home -i "$IFACE" -j ACCEPT

          $LOGGER -t nm-firewall "Connected to trusted network $TRUSTED_SSID: trusted interface $IFACE (all incoming ports accepted)"
        elif [ "$ACTION" = "down" ] || [ -n "$CONNECTION_ID" -a "$CONNECTION_ID" != "$TRUSTED_SSID" ]; then
          $IPT -F nixos-fw-home
          $IP6T -F nixos-fw-home
          $LOGGER -t nm-firewall "Untrusted or disconnected network ($CONNECTION_ID): restored strict firewall"
        fi
      '';
      type = "basic";
    }
  ];
```

---

## 4. Verification & Diagnostic Commands

### Inspect Active Chain Rules
```bash
# Verify sub-chain presence and active rules
sudo iptables -L nixos-fw-home -n -v
sudo ip6tables -L nixos-fw-home -n -v
```

### Inspect Dispatcher Logs
```bash
# Follow event logs from the dispatcher script
journalctl -t nm-firewall -e --no-pager
```

### Triggering State Transitions Manually
```bash
# Force NetworkManager to re-evaluate connection state
nmcli connection up VICTORIA
```

---

## 5. Outstanding Testing Items

- [ ] Verify packet delivery from mobile device over LAN while on `VICTORIA`.
- [ ] Verify AP client isolation status on local router if packets are dropped upstream.
- [ ] Verify transition when roaming to mobile hotspot (confirming chain flush).
- [ ] Verify behavior across system sleep/wake cycles (`systemd-suspend`).
