# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

### Raspberry Pi

- **IP:** 192.168.15.17
- **User:** melor
- **Key:** ~/.ssh/id_ed25519 (must specify with `-i` flag)
- **SSH Command:** `ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no melor@192.168.15.17`

**Setup steps:**
1. Add public key to Pi's `~/.ssh/authorized_keys`:
   ```bash
   ssh melor@192.168.15.17 "echo '$(cat ~/.ssh/id_ed25519.pub)' >> ~/.ssh/authorized_keys"
   ```
2. Always use `-i ~/.ssh/id_ed25519` (exec defaults to /var/root keys otherwise)

- Email for account: melorodrigo@gmail.com

### OpenClaw Source
- Docs: `/Users/rodrigomelo/projects/openclaw/docs`
- AGENTS.md: `/Users/rodrigomelo/projects/openclaw/AGENTS.md`

### OpenClaw TTS (Edge TTS)

- Provider: Edge TTS (free, no API key)
- Voice: pt-BR-AntonioNeural (Brazilian male)
- Language: pt-BR
- Config: `messages.tts.auto = always`
- Docs: `/projects/openclaw/docs/tts.md`

### Audio

**Transcription (speech-to-text):**
- Tool: `whisper` (OpenAI Whisper CLI)
- Model: turbo (local, free)
- Installed via: `brew install openai-whisper`

**Local TTS (fallback):**
- Tool: `say` (macOS built-in)
- Portuguese (BR) voice: "Luciana"
- English voice: "Samantha"

### Multi-Agent Setup (Olympian Family)

| Agent | God | Workspace | Purpose |
|-------|-----|-----------|---------|
| hermes | Hermes | ~/.openclaw/workspace | General assistant, orchestration, coordination |
| hefesto | Hefesto | ~/.openclaw/workspace-hefesto | Code, architecture, technical tasks |
| athena | Athena | ~/.openclaw/workspace-athena | UX Design, user research |
| apollo | Apollo | ~/.openclaw/workspace-apollo | Code review, testing, QA |
| artemis | Artemis | ~/.openclaw/workspace-artemis | Research, bug hunting, exploration |
| poseidon | Poseidon | ~/.openclaw/workspace-poseidon | Data pipelines, storage, infrastructure |
| dionysus | Dionysus | ~/.openclaw/workspace-dionysus | Creative brainstorming, content |
| hades | Hades | ~/.openclaw/workspace-hades | Archives, security, backups |
| demeter | Demeter | ~/.openclaw/workspace-demeter | Task automation, scheduling, productivity |

**Routing:** By Telegram account ID (see below)

### Telegram Accounts

| Account ID | Agent |
|------------|-------|
| default | hermes |
| hefesto | hefesto |
| athena | athena |
| apollo | apollo |
| artemis | artemis |
| poseidon | poseidon |
| dionysus | dionysus |
| hades | hades |
| demeter | demeter |

**Channel ID:** 316530505 (Rodrigo Melo)

### Family Relations

```
                    ⚡ ZEUS (king)
                       │
         ┌─────────────┼─────────────┐
         │             │             │
     HERMES        HEFESTO        POSEIDON
     (messenger)   (forge)        (sea)
         │             │             │
         │         ATHENA          │
         │         (wisdom)        │
         │             │             │
         │      ┌──────┴──────┐     │
         │      │             │     │
      APOLLO   ARTEMIS      HADES
      (sun)    (hunt)      (underworld)
         │
      DIONYSUS
      (wine)
         
      DEMETER
      (harvest)
```

### Collaboration Flow

1. **Athena designs** → Hefesto builds → Apollo tests → Hermes delivers
2. **Artemis hunts bugs** → Apollo reviews → Hefesto fixes
3. **Poseidon provides data** → Athena designs → Hefesto builds
4. **Dionysus generates ideas** → Athena refines → Hefesto implements
5. **Demeter automates** → Everything runs smoothly

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
