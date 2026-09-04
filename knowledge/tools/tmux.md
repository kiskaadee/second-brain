# Tmux Cheat Sheet & Quick Reference
From: https://tmuxcheatsheet.com/

**Note:** All keybinds assume the default prefix is `Ctrl + b`.

## Session Management

| **Action**                  | **Keybind**        | **Command**                                               |
| --------------------------- | ------------------ | --------------------------------------------------------- |
| **Start new session**       | -                  | `tmux`, `tmux new`, `tmux new-session`, `:new`            |
| **Start/Attach session**    | -                  | `tmux new-session -A -s <name>`                           |
| **New session (named)**     | -                  | `tmux new -s <name>`, `:new -s <name>`                    |
| **List sessions**           | `Ctrl + b s`       | `tmux ls`, `tmux list-sessions`                           |
| **Attach last session**     | -                  | `tmux a`, `tmux at`, `tmux attach`, `tmux attach-session` |
| **Attach specific session** | -                  | `tmux a -t <name>`, `tmux attach -t <name>`               |
| **Detach from session**     | `Ctrl + b d`       | -                                                         |
| **Detach others**           | -                  | `:attach -d`                                              |
| **Rename session**          | `Ctrl + b $`       | -                                                         |
| **Kill current session**    | -                  | `:kill-session`                                           |
| **Kill specific session**   | -                  | `tmux kill-ses -t <name>`                                 |
| **Kill all but current**    | -                  | `tmux kill-session -a`                                    |
| **Kill all but**            | -                  | `tmux kill-session -a -t <name>`                          |
| **Prev/Next session**       | `Ctrl + b (` / `)` | -                                                         |

## Pane Management

| **Action**                 | **Keybind**                  | **Command**               |
| -------------------------- | ---------------------------- | ------------------------- |
| **Split horizontally**     | `Ctrl + b %`                 | `:split-window -h`        |
| **Split vertically**       | `Ctrl + b "`                 | `:split-window -v`        |
| **Switch pane**            | `Ctrl + b arrow` / `h,j,k,l` | -                         |
| **Switch next pane**       | `Ctrl + b o`                 | -                         |
| **Toggle last pane**       | `Ctrl + b ;`                 | -                         |
| **Move pane left/right**   | `Ctrl + b {` / `}`           | -                         |
| **Toggle pane zoom**       | `Ctrl + b z`                 | -                         |
| **Resize pane**            | `Ctrl + b + arrow`           | -                         |
| **Show pane numbers**      | `Ctrl + b q`                 | -                         |
| **Select pane by num**     | `Ctrl + b q <num>`           | -                         |
| **Convert pane to window** | `Ctrl + b !`                 | -                         |
| **Close current pane**     | `Ctrl + b x`                 | -                         |
| **Toggle sync panes**      | -                            | `:setw synchronize-panes` |
| **Toggle layouts**         | `Ctrl + b Space`             | -                         |
| **Pane actions menu**      | `Ctrl + b >`                 | -                         |

## Copy Mode

|**Action**|**Keybind**|**Command**|
|---|---|---|
|**Enter copy mode**|`Ctrl + b [`|-|
|**Scroll page up**|`Ctrl + b PgUp`|-|
|**Enable vi mode**|-|`:setw -g mode-keys vi`|
|**Quit copy mode**|`q`|-|
|**Move cursor**|`h, j, k, l`|-|
|**Word move (fwd/bwd)**|`w` / `b`|-|
|**Top/Bottom of line**|`g` / `G`|-|
|**Scroll up/down**|`↑` / `↓`|-|
|**Search (fwd/bwd)**|`/` / `?`|-|
|**Search next/prev**|`n` / `N`|-|
|**Start selection**|`Spacebar`|-|
|**Copy selection**|`Enter`|-|
|**Clear selection**|`Esc`|-|
|**Paste buffer**|`Ctrl + b ]`|-|
|**Show buffer**|-|`:show-buffer`, `:list-buffers`|
|**Choose buffer**|-|`:choose-buffer`|
|**Capture entire pane**|-|`:capture-pane`|
|**Save buffer**|-|`:save-buffer <file>`|
|**Delete buffer**|-|`:delete-buffer -b <num>`|

## Misc & Help

|**Action**|**Keybind**|**Command**|
|---|---|---|
|**Command mode**|`Ctrl + b :`|-|
|**List key bindings**|`Ctrl + b ?`|`:list-keys`, `tmux list-keys`|
|**Session/Win preview**|`Ctrl + b w`|-|
|**Set global option**|-|`:set -g <option>`|
|**Set window option**|-|`:setw -g <option>`|
|**Enable mouse**|-|`:set mouse on`|
|**Print version**|-|`tmux -v`|
|**Show info**|-|`tmux info`|
