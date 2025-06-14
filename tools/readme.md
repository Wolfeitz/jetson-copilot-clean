# 🛠 Jetson Copilot Docker Tools

This directory contains Docker utility scripts to help you safely maintain and manage your Docker environment during development, builds, and deployment.

---

## 🚦 Overview of Tools

| Script | Purpose | When to Use | Safe? |
|--------|---------|-------------|-------|
| `docker_reset.sh` | Soft reset of Docker state | Before rebuilds, testing clean builds | ✅ Very safe |
| `docker_clean.sh` | Intermediate cleanup of unused resources | Periodically to reclaim disk space | ✅ Safe |
| `docker_nuke.sh` | Full destructive wipe of Docker system | Only for emergencies or major resets | ⚠ Use extreme caution |

---

## 🔧 Details & Usage

---

### 🔨 `docker_reset.sh`

✅ **Purpose:**
- Stops all running containers
- Removes all stopped containers
- Prunes unused volumes & images
- Leaves images you're still actively using

✅ **When to Use:**
- Before running a clean `./build_copilot.sh`  
- After you've tested one build, want to rebuild fully fresh
- Safe daily use during development

✅ **Usage:**

```bash
cd ~/Projects/jetson-copilot-clean/tools
./docker_reset.sh
```

### 🔨 `docker_clean.sh`
✅ Purpose:

- Aggressively removes:
    - Stopped containers
    - Dangling images
    - Unused volumes
    - Unused networks
- Leaves active containers and images untouched

✅ When to Use:

- When Docker is growing large but you don't want full wipes
- Periodic maintenance every few weeks
- Great for freeing up orphaned resources

✅ Usage:
```bash
cd ~/Projects/jetson-copilot-clean/tools
./docker_clean.sh
```
✅ Very safe — production-safe.

### 🔨 `docker_nuke.sh`
🚨 Purpose:
- Full factory reset of Docker system
- Deletes EVERYTHING:
    - Running containers
    - Stopped containers
    - Volumes
    - Networks
    - All Docker images

🚨 When to Use:
- Last resort if Docker system becomes corrupt
- To free up all disk space used by Docker
- Major environment rebuilds
- Changing storage locations (moving Docker to external disk)

⚠ Consequences:
- After running this, Docker will be empty — full rebuild required.
- You will need to re-pull all models, images, rebuild containers.

✅ Usage:
```bash
cd ~/Projects/jetson-copilot-clean/tools
./docker_nuke.sh
```
✅ You will be prompted to confirm before execution.

---

### 🔧 `✅ Quick Install Permissions (first time only)`
```bash
chmod +x docker_reset.sh docker_clean.sh docker_nuke.sh
```
### 📝 `Pro Tips`
- Always start with docker_reset.sh first.
- Only use docker_clean.sh occasionally.
- docker_nuke.sh is very powerful — only run if fully intended.

These tools were built to help during Jetson Copilot V3.1.3 SaaS-ready development cycles while staying friendly for both Jetson AGX Orin and future DGX-scale cluster builds.

