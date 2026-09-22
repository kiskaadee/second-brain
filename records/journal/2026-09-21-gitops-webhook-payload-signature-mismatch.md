---
type: journal
project: homelab
date: 2026-09-21
tags:
  - operations
  - homelab
  - troubleshooting
  - gitops
  - webhook
  - cryptography
  - gitea
  - nixos
---

# GitOps Dispatcher Webhook Signature Mismatch: Epistemic Root Cause Analysis

## 1. System Context & Fundamentals

The homelab appliance operates a continuous deployment pipeline designed to automatically keep workload directories (in `~/Sites`) and data vaults (such as `~/Brain`) synchronized with their authoritative Git remotes on Gitea (`gitea.roadtotech.me`).

```
                                      SERVER APPLIANCE (:9000)
                              ┌────────────────────────────────────────────────────────┐
┌──────────────┐              │ ┌──────────────────┐       ┌─────────────────────────┐ │       ┌──────────────────┐
│ Gitea Push   │──HTTP POST──►│ │ adnanh/webhook   │──────►│ gitops_dispatcher.py    │─┼──────►│ Target Worktree  │
│ Webhook Event│   (signed)   │ │ daemon (:9000)   │ argv  │ (HMAC verification)     │ │ git   │ (~/Brain)        │
└──────────────┘              │ └──────────────────┘       └─────────────────────────┘ │ pull  └──────────────────┘
                              └────────────────────────────────────────────────────────┘
```

### Components & Protocol Contracts
1. **Gitea Webhook Service**: According to Gitea's webhook implementation (`modules/webhook/webhook.go`), when a repository webhook is configured with a shared secret, Gitea calculates an HMAC-SHA256 digest over the **exact raw HTTP request body bytes** prior to transmission and delivers the bare hexadecimal digest in the `X-Gitea-Signature` HTTP header.
2. **Webhook Daemon (`adnanh/webhook`)**: A lightweight Go daemon running on internal port 9000 (managed via NixOS systemd unit `homelab-gitops.service`). It listens for incoming HTTP requests, extracts parameters, and passes them as arguments to execution scripts.
3. **GitOps Dispatcher (`gitops_dispatcher.py`)**: A Python engine that validates the payload HMAC-SHA256 signature against `/run/secrets/gitops/webhook_secret` (projected via SOPS), admits the target repository, and spawns an asynchronous worker to perform `git pull --ff-only`.

### Cryptographic Security Contract
Per RFC 2104 (HMAC), HMAC-SHA256 verification relies strictly on **byte-for-byte equality**:
$$\text{Signature} = \text{HMAC-SHA256}(\text{Shared Secret}, \text{Payload Bytes})$$
If even a single byte, whitespace character, or key ordering differs between the payload signed by Gitea and the payload evaluated by the Python dispatcher, the computed digest diverges completely due to the avalanche effect.

---

## 2. Problem & Observations

During routine operations, pushes to the `second-brain` repository on Gitea failed to trigger automatic synchronization in the server's working tree (`~/Brain`).

### Raw Observations (Machine Outputs)
1. **Working Tree State**: Inspecting `~/Brain` on `server` revealed the working tree was not updating automatically:
   ```text
   On branch main
   Your branch is behind 'origin/main' by 4 commits, and can be fast-forwarded.
     (use "git pull" to update your local branch)
   ```
2. **Initial Systemd Journal Trace**: Inspecting `homelab-gitops.service` logs revealed that the webhook daemon triggered the dispatcher script, but authentication failed closed:
   ```text
   webhook[4494]: executing /home/kiskaadee/Core/scripts/gitops_dispatcher.py with arguments [..., "<json>", "", "push"]
   webhook[4494]: [ERROR] [GitOps] Authentication failed: Missing signature header.
   webhook[4494]: [ERROR] [GitOps] ❌ Webhook authentication failed. Rejecting request.
   webhook[4494]: [webhook] error occurred: exit status 1
   ```
3. **Secondary Systemd Journal Trace (Post-Secret Configuration)**: After configuring the shared secret in Gitea repository settings and triggering a test delivery, the daemon received the signature header but failed cryptographic verification:
   ```text
   webhook[4494]: executing /home/kiskaadee/Core/scripts/gitops_dispatcher.py with arguments [..., "<json>", "c98657cbabeb6d7cf54f4868163d082d2dcb622a489f16c2549cc81549b26b83", "push"]
   webhook[4494]: [ERROR] [GitOps] Authentication failed: Signature mismatch.
   webhook[4494]: [ERROR] [GitOps] ❌ Webhook authentication failed. Rejecting request.
   ```

---

## 3. Diagnostic Inquiries & Investigation Progression

The investigation progressed through three distinct diagnostic inquiries as live evidence emerged:

### Phase 1: Investigating Missing Signature Header

* **Question**: Why was the second argument (the `X-Gitea-Signature` header) passed as an empty string `""` in the initial journal trace?
* **Inference**: In Gitea, if a webhook is created without a secret token, Gitea skips HMAC generation and omits the signature header entirely.
* **Test Command**: Query Gitea's SQLite database inside the `gitea` container:
  ```bash
  ssh server-local "docker exec gitea sqlite3 /data/gitea/gitea.db 'SELECT id, repo_id, url, secret FROM webhook;'"
  ```
* **Observed Evidence**:
  ```text
  1|6|http://192.168.1.36:9000/hooks/deploy||1|gitea
  ```
  The `secret` column for webhook ID 1 (`second-brain`) was empty (`""`).
* **Intervention**: Entered the SOPS shared secret into Gitea repository webhook settings.

---

### Phase 2: Investigating Signature Mismatch with Matching Credentials

* **Question**: Once the secret was added and Gitea transmitted a signature (`c98657cb...`), why did `hmac.compare_digest` fail?
* **Working Hypothesis 1 (Credential Discrepancy)**: The secret stored in Gitea's database did not match the decrypted secret file on the server host.
* **Discriminating Test**: Compare the SHA-256 digests of the Gitea database secret and the host secret in memory without logging raw credentials:
  ```python
  import hashlib
  # Safely verify credential equality
  db_secret_hash = hashlib.sha256(db_secret.encode("utf-8")).hexdigest()
  host_secret_hash = hashlib.sha256(host_secret_bytes.strip()).hexdigest()
  assert db_secret_hash == host_secret_hash
  ```
* **Observed Evidence**: The hashes matched identically, proving both endpoints possessed the exact same shared secret.
* **Status**: Credential discrepancy hypothesis **refuted**.

---

### Phase 3: Isolating Payload Transformation Across the Daemon Boundary

* **Question**: If the credentials are equal and the algorithm is HMAC-SHA256, at what boundary did the input bytes diverge?
* **Working Hypothesis 2 (Daemon Parameter Re-serialization)**: The webhook daemon (`adnanh/webhook`) modified the payload bytes when extracting command-line arguments.
* **Inspection**: Inspected the webhook hook definition in `Core/nixos/modules/homeserver.nix`:
  ```nix
  pass-arguments-to-command = [
    { source = "entire-payload"; }
    { source = "header"; name = "X-Gitea-Signature"; }
    { source = "header"; name = "X-Gitea-Event"; }
  ];
  ```
* **Empirical Demonstration in Python**:
  Extracted the exact JSON string passed to the dispatcher in `sys.argv[1]` and tested HMAC verification against the received signature:
  ```python
  import hashlib, hmac

  secret = b"<shared_secret>"
  # The payload string as passed to sys.argv[1] by adnanh/webhook:
  received_payload = """{"after":"00000000...","before":"00000000...",...}"""

  # 1. Digest calculated over dispatcher's input argument:
  calculated_mac = hmac.new(secret, received_payload.encode("utf-8"), hashlib.sha256).hexdigest()
  print("Calculated over argv[1]:", calculated_mac)
  print("Received Gitea Sig:      ", "c98657cbabeb6d7cf54f4868163d082d2dcb622a489f16c2549cc81549b26b83")
  # Result: 6882b1c8... != c98657cb... (Mismatch)
  ```
* **Documentation Verification**: According to `adnanh/webhook` documentation, `source: "entire-payload"` unmarshals JSON into a Go data structure and re-marshals it using Go's standard `json.Marshal`, altering key order and whitespace. Conversely, `source: "raw-request-body"` captures the unmodified byte stream received over the network.
* **Status**: Payload transformation hypothesis **confirmed**.

---

## 4. Findings & Root Cause Analysis

### The Underlying Mechanism
1. **Gitea Signing Stage**: Gitea calculates the HMAC-SHA256 digest on the literal byte sequence of the HTTP request body before transmission over TCP.
2. **Intermediate Parsing Stage**: `adnanh/webhook` with `source: "entire-payload"` parses the HTTP body into a generic `map[string]interface{}` and re-serializes it when constructing `sys.argv`.
3. **Serialization Divergence**: Go's `json.Marshal` sorts dictionary keys lexicographically and strips formatting whitespace. Consequently:
   $$\text{len}(\text{raw HTTP bytes}) \neq \text{len}(\text{re-marshaled bytes})$$
   $$\text{SHA256}(\text{raw HTTP bytes}) \neq \text{SHA256}(\text{re-marshaled bytes})$$
4. **Verification Failure**: The dispatcher received the re-marshaled string, computed HMAC over its bytes, and rejected the signature due to the byte-level discrepancy.
5. **Remediation Mechanism**: Declaring `source: "raw-request-body"` instructs `adnanh/webhook` to pass the unmodified raw byte buffer directly into the process argument.

---

## 5. Declarative Remediation & Local Validation

### Declarative NixOS Change
Modified [`Core/nixos/modules/homeserver.nix`](https://gitea.roadtotech.me/kiskaadee/homelab-core/src/branch/main/nixos/modules/homeserver.nix) to replace `entire-payload` with `raw-request-body`:

```diff
           id = "deploy";
           execute-command = "/home/kiskaadee/Core/scripts/gitops_dispatcher.py";
           pass-arguments-to-command = [
-            { source = "entire-payload"; }
+            { source = "raw-request-body"; }
             { source = "header"; name = "X-Gitea-Signature"; }
             { source = "header"; name = "X-Gitea-Event"; }
           ];
```

### Local Invariant Validation
Ran the repository pre-commit test suite and Nix flake evaluation:
```bash
./Core/scripts/test
```
*Output*: 35/35 pytest unit and security tests passed; flake derivation evaluated cleanly. Committed and pushed to `main` (`5f12e9e`).

---

## 6. Deployment Procedure & Post-Fix Verification

> [!IMPORTANT]
> **Privileged Operation Guardrail**: Applying host-level NixOS system configurations requires an operator with root/sudo privileges (`sudo nixos-rebuild switch`).

### Operator Rebuild Runbook
1. **SSH to the Server Appliance**:
   ```bash
   ssh server-remote
   ```
2. **Pull and Switch NixOS Configuration**:
   ```bash
   cd ~/Core && git pull origin main
   sudo nixos-rebuild switch --flake ~/Core#server
   ```
3. **Trigger Test Delivery**:
   In Gitea web UI, navigate to `https://gitea.roadtotech.me/kiskaadee/second-brain/settings/hooks` and click **Test Delivery**.
4. **Verify Dispatcher Journal**:
   ```bash
   journalctl -u homelab-gitops -n 20 --no-pager
   ```
   *Expected Result*: `✅ Webhook admission passed: Admitted for deployment on branch 'main'.`
5. **Verify Target Repository State**:
   Inspect `~/Brain` on the server host to confirm the working tree is fast-forwarded to `origin/main`.

---

## 7. Discussion & Transferable Lessons

### Transferable Diagnostic Heuristics
1. **Cryptographic Input Boundary Invariant**: When an intermediary process (proxy, API gateway, hook daemon) sits between a signing client and a verifying backend, the parameter extraction layer must preserve raw, unparsed byte streams. Never perform cryptographic signature validation on deserialized and re-serialized data.
2. **Systematic Signature Debugging**: When an HMAC verification fails despite identical secrets, follow this elimination sequence:
   - *Step 1 (Credential Identity)*: Verify secret synchronization using safe cryptographic hash comparisons.
   - *Step 2 (Algorithm & Encoding)*: Verify HMAC algorithm (SHA256 vs. SHA1), digest format (hex vs. Base64), and prefix handling (`sha256=` stripping).
   - *Step 3 (Byte-Level Identity)*: Capture the raw byte stream at the signer and the verifier to identify serialization, encoding, or newline mutations.

### Retrospective Architectural Analysis
* **Why the defect was latent**: The dispatcher was initially tested with manual CLI invocations (`--repo second-brain --branch main`), which bypass the HTTP webhook signature verification gate. Live webhook integration was the only layer subject to `adnanh/webhook`'s argument serialization behavior.

---

## 8. References
* [`Core/scripts/gitops_dispatcher.py`](https://gitea.roadtotech.me/kiskaadee/homelab-core/src/branch/main/scripts/gitops_dispatcher.py)
* [`Core/nixos/modules/homeserver.nix`](https://gitea.roadtotech.me/kiskaadee/homelab-core/src/branch/main/nixos/modules/homeserver.nix)
* [Brain GitOps & Auto-Sync Deployment Pipeline](../../projects/homelab/guides/brain-gitops-deployment-pipeline.md)
* [Scientific Incident Investigation & Epistemic Journaling](../../knowledge/methods/incident-investigation-and-journaling.md)
* [adnanh/webhook Hook Parameters Documentation](https://github.com/adnanh/webhook#hook-parameters)
* [RFC 2104: HMAC: Keyed-Hashing for Message Authentication](https://datatracker.ietf.org/doc/html/rfc2104)
