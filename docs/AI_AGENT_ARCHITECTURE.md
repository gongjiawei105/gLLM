# Where AI Coding Agents Stand: A Layered Systems Architecture

## 1. The Unified Operating System Stack

Every modern OS — Linux, Windows, macOS — shares the same fundamental layered architecture. Understanding these layers is key to understanding what AI agents can and cannot do.

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: Applications                                          │
│  Browser, VS Code, Docker Desktop, Claude Code, ChatGPT Codex  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: Shell / Command Interpreter                           │
│  bash (Linux), zsh (macOS), PowerShell/cmd (Windows)            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: System Libraries & Runtimes                           │
│  glibc, .NET, Python, Node.js, libc, Win32 API, Cocoa          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: OS Services & Daemons                                 │
│  systemd, Docker Engine, NetworkManager, launchd, svchost       │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Kernel                                                │
│  Linux kernel, Windows NT kernel, XNU/Darwin (macOS)            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 0: Hardware                                              │
│  CPU, GPU, RAM, Disk, Network Interface                         │
└─────────────────────────────────────────────────────────────────┘
```

### Layer-by-Layer Breakdown

| Layer | Linux | Windows | macOS | Role |
|-------|-------|---------|-------|------|
| **0 - Hardware** | Same | Same | Same | Physical compute, storage, network |
| **1 - Kernel** | Linux kernel | NT kernel | XNU (Darwin) | Process scheduling, memory management, device drivers, file systems, security enforcement |
| **2 - OS Services** | systemd, Docker Engine, cron | Services (svchost), WSL2 | launchd, Docker Desktop | Background processes that manage the system |
| **3 - Libraries** | glibc, libstdc++ | Win32 API, .NET | Cocoa, Core Foundation | Provide programming interfaces to kernel features |
| **4 - Shell** | bash, zsh, fish | PowerShell, cmd.exe | zsh, bash | Human-readable command interpreter — translates text commands into system calls |
| **5 - Applications** | VS Code, Firefox, Claude Code | VS Code, Chrome, Codex | VS Code, Safari, Claude Code | User-facing programs |

### Where Does the Shell Fit?

The shell is **Layer 4** — it sits between applications and the OS. It's the *translator*:

```
 You type: "rm -rf /tmp/old_files"
      │
      ▼
 ┌──────────────┐
 │  Shell (L4)  │  Parses the command, resolves paths
 └──────┬───────┘
        │ Calls unlink() system call for each file
        ▼
 ┌──────────────┐
 │  Kernel (L1) │  Checks permissions, removes filesystem entries
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │ Hardware (L0)│  Marks disk blocks as free
 └──────────────┘
```

**Why is the shell powerful?** It has direct access to system calls through the kernel. When you type `sudo`, the shell asks the kernel to elevate privileges. The kernel checks `/etc/sudoers` and either grants or denies.

**Why can Claude Code use bash?** Claude Code spawns a child process that runs bash. But the child process inherits Claude Code's restricted permissions — not yours.

```
Your Terminal Session (your user, can sudo)
    │
    └── Claude Code (sandboxed subprocess)
            │
            └── bash (child of Claude Code, inherits sandbox restrictions)
                  │
                  ├── git commit    ← works (no privilege needed)
                  ├── npm install   ← works (writes to user-owned dirs)
                  └── sudo docker   ← BLOCKED (no sudo access)
```

## 2. The Permission Hierarchy

Every process on any OS runs with a specific privilege level. Here's the full hierarchy:

```
Ring 0 ──── Kernel Mode ──────── Full hardware access
                                  Only the kernel runs here

Ring 3 ──── User Mode ───────── All applications run here
              │
              ├── root / Administrator ── can modify any file, any process
              │     │
              │     ├── sudo (Linux/macOS) ── temporary root elevation
              │     └── "Run as Administrator" (Windows) ── same concept
              │
              ├── Regular User ── can modify own files, own processes
              │     │
              │     ├── Your terminal ── runs as you (jzg317)
              │     ├── VS Code ── runs as you
              │     └── Docker commands ── need sudo on Linux (root-owned socket)
              │
              └── Sandboxed Process ── restricted subset of user permissions
                    │
                    ├── Claude Code ── can read/write files, run safe commands
                    ├── Browser tabs ── isolated from each other
                    └── Docker containers ── isolated filesystem & network
```

### Cross-Platform Privilege Comparison

| Action | Linux | Windows | macOS |
|--------|-------|---------|-------|
| Read own files | User | User | User |
| Install system packages | `sudo apt install` | Admin prompt | `sudo brew install` |
| Start Docker | `sudo docker` or docker group | Docker Desktop (Hyper-V) | Docker Desktop (HyperKit) |
| Modify system config | `sudo vim /etc/...` | Registry Editor (admin) | `sudo vim /etc/...` |
| Kill other users' processes | `sudo kill` | Task Manager (admin) | `sudo kill` |

## 3. Where AI Coding Agents Operate

### Claude Code — Layer 5 (Sandboxed Application)

```
┌─────────────────────────────────────────────────────┐
│                  Claude Code                         │
│                                                      │
│  Runs as: sandboxed subprocess of your IDE/terminal  │
│  Privilege: restricted user-level                    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  TOOLS (what Claude can invoke)              │    │
│  │                                              │    │
│  │  File System:                                │    │
│  │    Read  ─── kernel read() syscall ──► L1    │    │
│  │    Write ─── kernel write() syscall ──► L1   │    │
│  │    Edit  ─── read + write                    │    │
│  │    Glob  ─── kernel readdir() ──► L1         │    │
│  │    Grep  ─── read + regex match              │    │
│  │                                              │    │
│  │  Process Execution:                          │    │
│  │    Bash  ─── fork() + exec() ──► L1          │    │
│  │           └── inherits sandbox restrictions   │    │
│  │           └── no sudo, no interactive stdin   │    │
│  │                                              │    │
│  │  Network:                                    │    │
│  │    WebFetch ─── HTTP client ──► L3 ──► L1    │    │
│  │    WebSearch ── search API ──► L3 ──► L1     │    │
│  │                                              │    │
│  │  Git:                                        │    │
│  │    git add/commit/push ── via Bash tool      │    │
│  │    gh (GitHub CLI) ── via Bash tool           │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  WHY these work:                                     │
│  • File ops use kernel syscalls available to ANY     │
│    process — no special privilege needed              │
│  • Bash commands work if they don't need sudo        │
│  • Network works because sockets are user-level      │
│  • Git works because it's just file ops + network    │
│                                                      │
│  WHY these DON'T work:                               │
│  • sudo — requires password + PAM authentication     │
│  • docker — socket owned by root (on Linux)          │
│  • Interactive prompts — no stdin access              │
│  • Browser/GUI — no display server connection        │
└─────────────────────────────────────────────────────┘
```

### ChatGPT Codex — Cloud Sandbox (Isolated VM)

```
┌──────────────────────────────────────────────────────┐
│              Codex Cloud Sandbox                       │
│                                                       │
│  Runs as: disposable VM in OpenAI's cloud             │
│  Privilege: root inside the VM                        │
│                                                       │
│  ┌──────────────────────────┐  ┌───────────────────┐ │
│  │  VM (ephemeral)          │  │  Your Machine     │ │
│  │                          │  │                   │ │
│  │  ✓ sudo (root in VM)    │  │  NOT accessible   │ │
│  │  ✓ apt install           │  │  - no GPU         │ │
│  │  ✓ docker                │  │  - no local files │ │
│  │  ✓ any command           │  │  - no Docker      │ │
│  │                          │  │    containers     │ │
│  │  ✗ your GPU              │  │                   │ │
│  │  ✗ your database         │  │                   │ │
│  │  ✗ your running services │  │                   │ │
│  └──────────────────────────┘  └───────────────────┘ │
│                                                       │
│  Tradeoff: full control in isolation,                 │
│            but disconnected from your real system      │
└──────────────────────────────────────────────────────┘
```

### OpenHands (Open-Source Agent) — User-Level with Sudo

```
┌──────────────────────────────────────────────────────┐
│              OpenHands Architecture                    │
│                                                       │
│  Runs as: agent in Docker container on YOUR machine   │
│  Privilege: root inside container, optional host mount │
│                                                       │
│  ┌──────────────────────────────────────────────┐    │
│  │  Agent Container                              │    │
│  │                                               │    │
│  │  ✓ sudo (root in container)                   │    │
│  │  ✓ apt install (in container)                 │    │
│  │  ✓ full terminal emulation                    │    │
│  │  ✓ interactive prompts                        │    │
│  │  ✓ access mounted host directories            │    │
│  │                                               │    │
│  │  Configurable access to:                      │    │
│  │    ○ Host filesystem (via volume mounts)      │    │
│  │    ○ Host network (via --network host)        │    │
│  │    ○ Host Docker (via socket mount)           │    │
│  │    ○ GPU (via --gpus all)                     │    │
│  └──────────────────────────────────────────────┘    │
│                                                       │
│  Tradeoff: maximum capability,                        │
│            maximum risk (mistakes are real)            │
└──────────────────────────────────────────────────────┘
```

### OpenClaw — Local Personal AI Agent (openclaw.ai)

```
┌──────────────────────────────────────────────────────┐
│              OpenClaw Architecture                     │
│                                                       │
│  Runs as: persistent local agent on YOUR machine      │
│  Interface: WhatsApp, Telegram, Discord, Slack, etc.  │
│  Privilege: full user-level (configurable sandboxing) │
│                                                       │
│  ┌──────────────────────────────────────────────┐    │
│  │  Local Agent Process                          │    │
│  │                                               │    │
│  │  ✓ File system read/write                     │    │
│  │  ✓ Shell command execution                    │    │
│  │  ✓ Browser automation (navigate, fill forms)  │    │
│  │  ✓ 50+ service integrations (Gmail, GitHub,   │    │
│  │    Spotify, calendars, etc.)                   │    │
│  │  ✓ Persistent memory across conversations     │    │
│  │  ✓ Self-extending (can write own plugins)     │    │
│  │                                               │    │
│  │  LLM backend (user's choice):                 │    │
│  │    ○ Claude API                               │    │
│  │    ○ GPT API                                  │    │
│  │    ○ Local models                             │    │
│  │                                               │    │
│  │  Key difference from Claude Code:             │    │
│  │    - NOT IDE-integrated — runs as standalone   │    │
│  │    - Operates via chat apps (WhatsApp, etc.)  │    │
│  │    - Designed for general automation, not      │    │
│  │      just coding tasks                        │    │
│  │    - Persistent agent (always running)        │    │
│  │    - Configurable: full access OR sandboxed   │    │
│  └──────────────────────────────────────────────┘    │
│                                                       │
│  Tradeoff: broad automation + chat interface,         │
│            but user must trust agent with system access│
└──────────────────────────────────────────────────────┘
```

## 4. Comparative Analysis

### Capability Matrix

| Capability | Claude Code | Codex | OpenHands | OpenClaw | Your Terminal |
|-----------|-------------|-------|-----------|----------|---------------|
| Read/write files | Local | In VM | In container + host | Local | Local |
| Run bash commands | Yes (no sudo) | Yes (full) | Yes (full) | Yes (configurable) | Yes (full) |
| sudo / root access | No | In VM only | In container | Configurable | Yes |
| Access local GPU | No (indirectly via files) | No | Yes (configurable) | Yes | Yes |
| Access local Docker | No | No | Yes (configurable) | Yes | Yes |
| Access local database | Via code only | No | Yes | Yes | Yes |
| Internet access | WebFetch/WebSearch | Limited | Yes | Yes (50+ integrations) | Yes |
| Interactive prompts | No | Yes | Yes | Yes (via chat apps) | Yes |
| See browser/GUI | No | No | VNC possible | Yes (browser automation) | Yes |
| Git operations | Yes | Yes | Yes | Yes | Yes |
| Persist changes | To your repo | PR/branch | To your repo | To your repo | To your repo |
| Interface | IDE/Terminal | Web UI | Web UI | WhatsApp/Telegram/etc. | Terminal |
| Always running | No (session-based) | No (task-based) | No (session-based) | Yes (persistent daemon) | Yes |

### Risk Matrix

| Risk Factor | Claude Code | Codex | OpenHands | OpenClaw |
|------------|-------------|-------|-----------|----------|
| Accidental file deletion | Low (human reviews) | None (VM is disposable) | High (changes are real) | High (changes are real) |
| Breaking system config | Not possible (no sudo) | Not possible (isolated) | Possible (has sudo) | Possible (if configured) |
| Exposing secrets | Low (can read .env but sandboxed) | Low (isolated VM) | Medium (has network + files) | High (50+ service integrations) |
| Runaway processes | Low (commands time out) | Low (VM has limits) | Medium (container limits) | Medium (persistent daemon) |
| Wrong destructive command | Not possible (no sudo) | Contained in VM | Real damage possible | Real damage possible |
| Unauthorized external actions | Not possible | Not possible | Low (local only) | High (can send messages, emails, etc.) |

### The System Call Path: Why Claude Code Can Read Files But Not Run Docker

Every tool Claude Code uses ultimately goes through the same path:

```
Claude Code Tool          System Call        Kernel Check         Result
─────────────────         ───────────        ────────────         ──────

Read("server.py")    →    read()        →   User owns file?  →   ✓ OK
Write("server.py")   →    write()       →   User owns file?  →   ✓ OK
Bash("git commit")   →    fork()+exec() →   git is in PATH?  →   ✓ OK
Bash("npm install")  →    fork()+exec() →   write to ./node_  →   ✓ OK
                                             modules/?
WebFetch(url)        →    socket()+     →   Port 443 access?  →   ✓ OK
                          connect()
Bash("sudo docker")  →    fork()+exec() →   PAM auth for     →   ✗ DENIED
                                             sudo? No tty,
                                             no password
Bash("docker ps")    →    fork()+exec() →   /var/run/docker.  →   ✗ DENIED
                                             sock readable?
                                             (root:docker)
```

## 5. The Docker Layer: Virtual OS Within an OS

Docker deserves special attention because it creates a new "mini-OS" inside the host:

```
┌─────────────────────────────────────────────────────────┐
│  Host OS (your machine)                                  │
│                                                          │
│  Host Kernel (Linux) ◄──── shared by all containers     │
│       │                                                  │
│       ├── Host Process: Claude Code (sandboxed)          │
│       │                                                  │
│       ├── Host Process: Docker Engine (runs as root)     │
│       │       │                                          │
│       │       ├── Container: PostgreSQL                   │
│       │       │   ├── Own filesystem (/) ← isolated     │
│       │       │   ├── Own network (172.17.x.x)          │
│       │       │   ├── Own process tree (PID 1 = postgres)│
│       │       │   └── Shared: host kernel, host GPU*    │
│       │       │                                          │
│       │       ├── Container: vLLM                        │
│       │       │   ├── Own filesystem                     │
│       │       │   ├── Own network                        │
│       │       │   ├── GPU passthrough (--gpus all)       │
│       │       │   └── Shared: host kernel, host GPU      │
│       │       │                                          │
│       │       └── Container: ChromaDB                    │
│       │           ├── Own filesystem                     │
│       │           └── Own network                        │
│       │                                                  │
│       └── Host Process: Your Terminal                     │
│               └── Can talk to Docker Engine via socket    │
│                   (requires root or docker group)         │
└─────────────────────────────────────────────────────────┘

* On Windows/macOS, Docker runs inside a lightweight Linux VM
  (WSL2 on Windows, HyperKit on macOS), adding one more layer:

  Windows: Hardware → NT Kernel → WSL2 VM → Linux Kernel → Docker → Container
  macOS:   Hardware → XNU → HyperKit VM → Linux Kernel → Docker → Container
  Linux:   Hardware → Linux Kernel → Docker → Container  (most direct)
```

## 6. Summary: Where Each Agent Sits

```
┌──────────────────────────────────────────────────────────────┐
│                                                               │
│   KERNEL SPACE (Ring 0)                                       │
│   ┌─────────────────────────────────────────────────────┐    │
│   │  Linux / NT / XNU Kernel                             │    │
│   │  - Process scheduling, memory, filesystems, drivers  │    │
│   └─────────────────────────────────────────────────────┘    │
│                                                               │
│   USER SPACE (Ring 3)                                         │
│                                                               │
│   root ─────────────────────────────────────────────────      │
│   │  Docker Engine, systemd, kernel modules                   │
│   │                                                           │
│   your user ────────────────────────────────────────────      │
│   │  Your terminal (bash/zsh/PowerShell)                      │
│   │  ├── sudo → temporary root escalation                     │
│   │  ├── docker → talks to Docker Engine                      │
│   │  └── any command you type                                 │
│   │                                                           │
│   │  ┌─────────────────────────────────┐                      │
│   │  │  OpenHands Agent Container       │                     │
│   │  │  - root INSIDE container         │  ◄── mimics you     │
│   │  │  - can mount your filesystem     │      highest AI     │
│   │  │  - can access your GPU           │      authority      │
│   │  └─────────────────────────────────┘                      │
│   │                                                           │
│   │  ┌─────────────────────────────────┐                      │
│   │  │  OpenClaw Agent                  │                     │
│   │  │  - full user-level access        │  ◄── broad auto-   │
│   │  │  - shell, files, browser         │      mation via     │
│   │  │  - 50+ service integrations      │      chat apps      │
│   │  │  - persistent (always running)   │      (configurable) │
│   │  └─────────────────────────────────┘                      │
│   │                                                           │
│   sandboxed ────────────────────────────────────────────      │
│   │  ┌─────────────────────────────────┐                      │
│   │  │  Claude Code                     │                     │
│   │  │  - file read/write               │  ◄── software-level │
│   │  │  - bash (no sudo)                │      safest AI      │
│   │  │  - git, npm, network             │      authority      │
│   │  │  - WebFetch, WebSearch           │                     │
│   │  └─────────────────────────────────┘                      │
│   │                                                           │
│   cloud ────────────────────────────────────────────────      │
│      ┌─────────────────────────────────┐                      │
│      │  Codex (OpenAI)                  │                     │
│      │  - root in disposable VM         │  ◄── full control   │
│      │  - no access to your machine     │      but isolated   │
│      │  - results returned as PR/code   │      from you       │
│      └─────────────────────────────────┘                      │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## 7. Key Takeaways

1. **The shell (bash) is a translator** between human-readable commands and kernel system calls. Every AI agent that runs commands uses the shell.

2. **Claude Code operates at Layer 5 (application)** with restricted Layer 4 (shell) access. It can invoke system calls for file I/O and process execution, but the kernel's permission checks block privilege escalation.

3. **Docker creates Layer 1-4 isolation** within the host kernel. Containers get their own filesystem, network, and process tree, but share the host kernel. This is why OpenHands can have root inside a container without compromising the host.

4. **The fundamental tradeoff** across all AI agents is:
   - **More authority = more capability = more risk**
   - Claude Code chose safety (sandboxed, human confirms dangerous ops)
   - OpenHands chose capability (full access in container, real consequences)
   - OpenClaw chose breadth (persistent agent, 50+ integrations, chat interface)
   - Codex chose isolation (full access in disposable VM, no real-system access)

5. **No mainstream AI tool operates at kernel level (Ring 0)**. This would mean the AI could modify the OS itself — loading drivers, changing security policies, modifying the bootloader. This remains a hard boundary that no vendor has crossed.

---

*Document generated during the gLLM project deployment, March 2026.*
*Based on practical experience deploying a full-stack LLM platform (PostgreSQL + ChromaDB + vLLM + FastAPI + React) using Claude Code with human-in-the-loop for system-level operations.*
