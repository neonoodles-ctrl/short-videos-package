# Setup prompt

The easy way: send your coding agent the repository link, "Set this up for me:
https://github.com/neonoodles-ctrl/short-videos-package". The agent clones it and follows
the steps below.

Or copy everything below the line into your coding agent (Claude Code, Codex, Cursor,
opencode, Aider, or any agent that can run shell commands).

**Agents:** if a user gave you only the link, everything below the line is your
instructions. Do step 0, then the rest in order.

---

You are setting up **short-videos-package** on this computer so I can make 90-second to
3-minute AI videos: still pictures, a song, animated clips, and a finished cut. Read
`AGENTS.md` and `docs/MODELS.md` in this repository first. Then do these steps in order.
Ask me only the questions marked **Ask**. Each **Ask** is a stop: ask, then wait for my
answer before doing anything else. Never choose for me. If you cannot ask questions in this
session (for example a one-shot or headless run), end your reply with the question and stop.
Never put ComfyUI, models or Obsidian inside this repository folder.

0. **Get the repository.** If you are not already inside a clone of
   https://github.com/neonoodles-ctrl/short-videos-package, clone it into the current folder
   (or the folder I name): `git clone https://github.com/neonoodles-ctrl/short-videos-package.git`,
   then work from inside the clone. Install git first if it is missing.

1. **Check the machine.** Report the operating system, the GPU and its VRAM, system RAM, and
   free disk space. Use `nvidia-smi` on NVIDIA, `rocm-smi` on AMD, and System Information on
   macOS. Do not install anything yet.

2. **Ask: local, API, or both?** Explain the routes from `docs/MODELS.md` in one short table:
   - `local-16gb`: GPUs with up to 16 GB. Flux.2 Klein 9B stills, Wan 2.2 clips, ACE-Step 1.5
     songs. Characters do not sing on screen; the song plays as a voiceover.
   - `local-24gb`: 24 GB or more. Adds MiniMax H3 clips, where a character can sing on screen
     in time with the song, and MiniMax Music 3 songs.
   - `fal`: any computer, pay per use with your own fal.ai key. Klein 9B stills, H3 clips
     (singing works), MiniMax Music 3 or ACE-Step songs.
   Recommend the route that fits the GPU you found. Mixed is fine, for example local stills
   and songs with fal clips. Then stop: install nothing until I have chosen.

3. **Install ComfyUI**, outside this folder, unless it is already installed (look for the
   ComfyUI desktop app, a portable folder, or a git checkout, and use that one). Follow the
   official instructions for this operating system:
   - Desktop app (Windows, macOS): https://www.comfy.org/download
   - Manual install (Linux, Windows, macOS): https://github.com/comfyanonymous/ComfyUI#installing
   - Windows portable: https://docs.comfy.org/installation/comfyui_portable_windows
   Update ComfyUI to the newest release: these workflows need its built-in Flux.2, Wan 2.2,
   ACE-Step 1.5, MiniMax H3 and MiniMax Music 3 nodes. Start it and confirm
   `http://127.0.0.1:8188` answers. Tell me the address if it uses another port.

4. **Download the models for the chosen route** from the links in `docs/MODELS.md`, into
   the ComfyUI `models/` subfolder each row names. Download only what the route needs, and
   tell me the total size before you start. Flux.2 Klein 9B is gated: **Ask** me to accept
   its licence on Hugging Face and to give you a Hugging Face token (keep it in an
   environment variable, never in a file in this repository).

5. **fal route only.** Install the ComfyUI-fal-API custom nodes
   (https://github.com/gokayfem/ComfyUI-fal-API) through ComfyUI-Manager or by cloning them
   into `ComfyUI/custom_nodes/`. **Ask** me for my fal key and set it as the `FAL_KEY`
   environment variable for ComfyUI. Never write it into this repository. Restart ComfyUI.

6. **Python tools.** In this repository, create a virtual environment and install the
   scripts' one dependency: `python -m venv .venv`, activate it, then
   `pip install -r requirements.txt`. Check that `ffmpeg` and `ffprobe` are installed; if
   not, install them with the system's package manager.

7. **Ask: do you want Obsidian for the storyboard?** Obsidian (https://obsidian.md/download)
   shows `scripts/storyboard.py`'s canvas: one card per shot with its lines, still and clip.
   If yes, install it and tell me to open this repository folder (or my projects folder) as a
   vault. If no, skip it; the storyboard is optional.

8. **Ask: how do you want to review the work?**
   - **Agent Previewer** (https://github.com/neonoodles-ctrl/agent-previewer): a local review
     desk. Agents submit stills, songs and cuts; you watch them, pin notes to moments, and
     approve. Install it by its README (outside this folder), start it, and confirm
     `previewer submit` works.
   - **Your own choice**: I tell you where to put files or which tool to use.
   - **None**: you look at files in `output/` yourself.
   Write my answer into `AGENTS.local.md` (git-ignored) so later sessions use it.

9. **Check every workflow of the route** against the running ComfyUI:
   `python scripts/run_workflow.py workflows/<route-folder>/<file>.api.json --check`
   If a model is in a subfolder under a different path, the check prints the `--set` to use.
   Fix every problem it reports before going on.

10. **One small test per workflow.** Use `examples/momos-one-kind-word/` (its reference
    image and prompts). Make one still, one 5-second clip from that still, and one 30-second
    song. On the fal route, tell me the cost of each test first (fal prices are per second or
    per megapixel) and wait for my OK. Look at every result yourself, then show them to me in
    the review tool from step 8.

11. **Report**: route, ComfyUI address, what was installed and where, total download size,
    each test's file and how long it took, and anything that failed. Then stop. To make a
    real video, I will ask you to follow `AGENTS.md`.
