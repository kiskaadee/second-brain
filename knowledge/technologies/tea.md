---
type: knowledge
status: stable
topics: ['gitea', 'cli']
---

# 🍵 Tea CLI (Gitea) Quick Reference & Fundamentals

## 📌 Overview
`tea` is the official command-line interface for **Gitea**. For engineers accustomed to GitHub's `gh` CLI, `tea` provides a nearly identical philosophy: it is **repository- and context-aware**, allowing you to manage repositories, issues, pull requests, releases, and milestones directly from your terminal without opening a web browser.

---

## 🔑 Authentication & Quick Setup

Unlike `gh` which targets a single global cloud service (`github.com`), `tea` can manage multiple self-hosted instances.

### 1. Authenticate with Gitea Instance
Run interactive login:
```bash
tea login add
```

**Prompts:**
* **URL of Gitea instance**: `https://gitea.roadtotech.me`
* **Name of new Login**: `roadtotech` (or your username / instance alias)
* **Login with**: `token`
* **Token**: Generate an access token via Gitea Web UI:
  - Navigate to **Settings** $\rightarrow$ **Applications** $\rightarrow$ **Generate New Token**.
  - Select scopes: `repo`, `issue`, `user`, `package`.
* **Set Optional settings**: `true`
* **SSH Key Path**: Leave empty for auto-discovery (e.g., `~/.ssh/id_ed25519`).
* **Allow Insecure connections**: `false` (valid HTTPS certificate via Traefik).
* **Add git helper**: `false` on NixOS (see gotcha below) or `true` if your Git config is mutable.
* **Check version of Gitea instance**: `true`.

### 2. Verify Authentication
```bash
# Check saved logins and active default
tea login list

# Verify current identity and connection
tea whoami

# Set default instance if you manage multiple
tea login default <login-name>
```

### 3. NixOS / Home Manager Gotcha: `exit status 255` (Read-only Git Config)

#### The Error
When setting `Add git helper: true` during `tea login add`, you may see:
```text
Login as <user> on https://<url> successful. Added this login as <user>
Error: error adding login: git config --global credential.https://<url>.helper, error: exit status 255
```

#### Why It Happens
`tea` attempts to register itself as a Git credential helper by executing:
```bash
git config --global credential.https://<url>.helper ...
```
On **NixOS** where Git is managed declaratively via Home Manager, `~/.config/git/config` is a symlink pointing to an immutable file in the `/nix/store`:
```text
~/.config/git/config -> /nix/store/...-home-manager-files/.config/git/config
```
Because the `/nix/store` is read-only, Git fails to acquire a write lock (`error: could not lock config file ... Read-only file system`) and exits with code `255`.

#### Key Takeaways & Resolution
1. **The login itself still succeeded:** `tea` stores its own configuration in `$XDG_CONFIG_HOME/tea/config.yml` (writable user space). You can verify this immediately with `tea login list`.
2. **If you authenticate Git operations via SSH (Recommended):** You do not need the HTTPS Git credential helper. Select `Add git helper: false` during setup (or ignore the exit status 255 error).
3. **If you want Git to use `tea` for HTTPS operations:** Declare the credential helper in your Home Manager configuration instead of letting `tea` mutate it at runtime:
   ```nix
   programs.git = {
     enable = true;
     extraConfig = {
       "credential \"https://gitea.roadtotech.me\"" = {
         helper = "tea login helper";
       };
     };
   };
   ```

---

## 🔄 `gh` vs `tea` Rosetta Stone

| Action | GitHub CLI (`gh`) | Gitea CLI (`tea`) |
| :--- | :--- | :--- |
| **Authentication** | `gh auth login` | `tea login add` |
| **Session Status** | `gh auth status` | `tea whoami` / `tea login list` |
| **Clone Repository** | `gh repo clone <owner>/<repo>` | `tea clone <owner>/<repo>` |
| **Create Remote Repo** | `gh repo create <name> --private` | `tea repo create --name <name> --private` |
| **Open in Web Browser** | `gh repo view --web` / `gh browse` | `tea open` |
| **List Issues** | `gh issue list` | `tea issues` *(or `tea issue ls`)* |
| **Create Issue** | `gh issue create` | `tea issue create` |
| **View Issue** | `gh issue view <id>` | `tea issue <id>` |
| **Close Issue** | `gh issue close <id>` | `tea issue close <id>` |
| **List Pull Requests** | `gh pr list` | `tea pulls` *(or `tea pr ls`)* |
| **Create Pull Request** | `gh pr create` | `tea pull create` |
| **Checkout PR Branch** | `gh pr checkout <id>` | `tea pull checkout <id>` |
| **View Pull Request** | `gh pr view <id>` | `tea pull <id>` |
| **Merge Pull Request** | `gh pr merge <id>` | `tea pull merge <id>` |
| **List Releases** | `gh release list` | `tea releases` |
| **Create Release** | `gh release create <tag>` | `tea release create --tag <tag>` |

---

## 🛠️ Everyday Workflows

### 1. Repositories (`tea repo` / `tea clone` / `tea open`)
`tea` inspects the local Git remotes. When run inside a cloned repo, commands automatically target that repository.

```bash
# Clone a repository from your instance
tea clone kiskaadee/nixos-config

# Initialize an existing local folder as a Gitea repository
git init
tea repo create --name my-app --private --init=false
git remote add origin https://gitea.roadtotech.me/kiskaadee/my-app.git
git push -u origin main

# Open current repo in the browser
tea open

# Fork an existing repository
tea repo fork upstream-owner/repo-name
```

---

### 2. Issues (`tea issues` / `tea issue`)

```bash
# List open issues for the current repository
tea issues

# Filter issues by author, state, or label
tea issues --state closed
tea issues --author kiskaadee
tea issues --labels bug,backend

# Interactively create a new issue (opens $EDITOR for markdown description)
tea issue create

# Create an issue inline with flags
tea issue create --title "Database pool connection timeout" --description "Observed 504 on /metrics."

# View issue details, comments, and status
tea issue 42

# Close or reopen an issue
tea issue close 42
tea issue reopen 42
```

---

### 3. Pull Requests (`tea pulls` / `tea pull`)

```bash
# List open pull requests
tea pulls

# Create a pull request from the active feature branch against main
tea pull create --title "feat: implement prometheus metrics" --target main

# Checkout a pull request locally for testing / review
tea pull checkout 15

# View PR details and diff status
tea pull 15

# Review and approve a pull request
tea pull approve 15

# Merge a pull request with specific merge strategy
tea pull merge 15 --style squash
# Available styles: merge, rebase, rebase-merge, squash
```

---

### 4. Releases & Tags (`tea releases` / `tea release`)

```bash
# List releases
tea releases

# Create a new release with an attached binary / asset
tea release create --tag v1.0.0 --title "Release v1.0.0" --asset ./build/output.tar.gz
```

---

## 💡 Advanced Tips & Power Features

### Targeting Repositories Explicitly
When executing commands outside of a repository directory, pass the `-R` or `--repo` flag:
```bash
tea issues -R kiskaadee/Brain
tea pulls -R kiskaadee/nixos-config
```

### Scripting & Structured Output
`tea` supports structured output formats for piping into `jq` or shell scripts:
```bash
# YAML output
tea pulls --output yaml

# JSON output
tea issues --output json | jq '.[] | {index: .index, title: .title}'
```

### Shell Autocompletion
To enable autocompletion for `tea` in your interactive shell:
```bash
# In ~/.bashrc or Nix Home Manager bash configuration
source <(tea completion bash)
```
