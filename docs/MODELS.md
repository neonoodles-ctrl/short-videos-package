# Models, routes and downloads

Nothing here is stored in this repository. Each file goes into your ComfyUI `models/`
folder, in the subfolder the table names (for example `ComfyUI/models/diffusion_models/`).
Sizes are the download sizes. Read each model's licence before you publish or sell videos.

## Pick a route

| Route | Graphics card | Stills | Clips | Songs | Singing on screen | Models to download |
|---|---|---|---|---|---|---|
| `local-16gb` | up to 16 GB VRAM (tested on a 16 GB RTX 4080) | Flux.2 Klein 9B | Wan 2.2 I2V A14B, 4-step | ACE-Step 1.5 XL | no: the song plays as a voiceover | about 76 GB |
| `local-24gb` | 24 GB VRAM or more | Flux.2 Klein 9B | MiniMax H3 (and Wan 2.2) | ACE-Step 1.5 XL or MiniMax Music 3 | yes, with `clip-h3-sing` | about 76 GB + 55 GB |
| `fal` | any computer | Klein 9B on fal | H3 Max on fal | MiniMax Music 3 or ACE-Step on fal | yes, with `clip-h3-sing-fal` | none; pay per use |

You can mix routes: for example local stills and songs with fal clips.

## local-16gb

| File | Folder | Size | Used by | Link |
|---|---|---|---|---|
| flux-2-klein-9b-fp8.safetensors | diffusion_models | 9.4 GB | still, edit | [Hugging Face](https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-fp8/resolve/main/flux-2-klein-9b-fp8.safetensors) (gated: accept the licence first) |
| qwen_3_8b_fp8mixed.safetensors | text_encoders | 8.7 GB | still, edit | [Hugging Face](https://huggingface.co/Comfy-Org/flux2-klein-9B/resolve/main/split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors) |
| flux2-vae.safetensors | vae | 0.3 GB | still, edit | [Hugging Face](https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors) |
| wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors | diffusion_models | 14.3 GB | clip-wan22-i2v | [Hugging Face](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors) |
| wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors | diffusion_models | 14.3 GB | clip-wan22-i2v | [Hugging Face](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors) |
| wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors | loras | 1.2 GB | clip-wan22-i2v | [Hugging Face](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors) |
| wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors | loras | 1.2 GB | clip-wan22-i2v | [Hugging Face](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors) |
| umt5_xxl_fp8_e4m3fn_scaled.safetensors | text_encoders | 6.7 GB | clip-wan22-i2v | [Hugging Face](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors) |
| wan_2.1_vae.safetensors | vae | 0.3 GB | clip-wan22-i2v | [Hugging Face](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors) |
| acestep_v1.5_xl_sft_bf16.safetensors | diffusion_models | 10.0 GB | song-ace-step15 | [Hugging Face](https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/diffusion_models/acestep_v1.5_xl_sft_bf16.safetensors) |
| qwen_0.6b_ace15.safetensors | text_encoders | 1.2 GB | song-ace-step15 | [Hugging Face](https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/text_encoders/qwen_0.6b_ace15.safetensors) |
| qwen_4b_ace15.safetensors | text_encoders | 8.4 GB | song-ace-step15 | [Hugging Face](https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/text_encoders/qwen_4b_ace15.safetensors) |
| ace_1.5_vae.safetensors | vae | 0.3 GB | song-ace-step15 | [Hugging Face](https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/vae/ace_1.5_vae.safetensors) |

**Smaller song model (cards under 12 GB):** swap in `acestep_v1.5_turbo.safetensors`
(4.8 GB, [link](https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/diffusion_models/acestep_v1.5_turbo.safetensors))
and `qwen_1.7b_ace15.safetensors` (3.7 GB, [link](https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/text_encoders/qwen_1.7b_ace15.safetensors)),
then run the song workflow with
`--set 1.unet_name=acestep_v1.5_turbo.safetensors --set 2.clip_name2=qwen_1.7b_ace15.safetensors --set 10.steps=8 --set 10.cfg=1`.
These are the settings of ComfyUI's own ACE-Step 1.5 template; this package was not tested with them.

## local-24gb (in addition to local-16gb)

The H3 turbo LoRA must be a version made for the pruned H3 model. Another copy with the
same weights (Abiray's `minimax_h3_turbo_4step_ckpt600_ema_V4.safetensors`) has 64 extra
bytes at the end of the file, and ComfyUI refuses to load it.

| File | Folder | Size | Used by | Link |
|---|---|---|---|---|
| minimax_h3_fl2va_pruned_int8_convrot.safetensors | diffusion_models | 21.0 GB | clip-h3, clip-h3-sing | [Hugging Face](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors) |
| minimax_h3_turbo_v4_step600_ema_comfy_pruned.safetensors | loras | 0.6 GB | clip-h3, clip-h3-sing | [Hugging Face](https://huggingface.co/QrusherZA/H3_Turbo_ComfyUI/resolve/main/minimax_h3_turbo_v4_step600_ema_comfy_pruned.safetensors) |
| qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors | text_encoders | 15.7 GB | clip-h3, clip-h3-sing | [Hugging Face](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors) |
| minimax_h3_video_vae_int8_convrot.safetensors | vae | 2.8 GB | clip-h3, clip-h3-sing | [Hugging Face](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_int8_convrot.safetensors) |
| minimax_h3_audio_vae_fp32.safetensors | vae | 0.6 GB | clip-h3, clip-h3-sing | [Hugging Face](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors) |
| minimax_music3_dit_fp16.safetensors | diffusion_models | 4.9 GB | song-minimax-music3 | [Hugging Face](https://huggingface.co/Comfy-Org/MiniMax-Music-3/resolve/main/diffusion_models/minimax_music3_dit_fp16.safetensors) |
| minimax_music3_text_encoder_pruned_int8_convrot.safetensors | text_encoders | 9.2 GB | song-minimax-music3 | [Hugging Face](https://huggingface.co/Comfy-Org/MiniMax-Music-3/resolve/main/text_encoders/minimax_music3_text_encoder_pruned_int8_convrot.safetensors) |
| minimax_music3_dav.safetensors | vae | 0.2 GB | song-minimax-music3 | [Hugging Face](https://huggingface.co/Comfy-Org/MiniMax-Music-3/resolve/main/vae/minimax_music3_dav.safetensors) |

## fal

No model files. Install the [ComfyUI-fal-API](https://github.com/gokayfem/ComfyUI-fal-API)
custom nodes and give ComfyUI your fal key as the `FAL_KEY` environment variable. Prices
checked on 2026-10-31 with fal's pricing API (they change; check before a batch):

| Workflow | fal endpoint | Price | Example |
|---|---|---|---|
| still-klein9b-fal, edit-klein9b-fal | fal-ai/flux-2/klein/9b/edit | USD 0.011 per megapixel (input + output) | one 1664x960 still from one reference: about USD 0.03 |
| clip-h3-fal, clip-h3-sing-fal | minimax/h3-max/image-to-video | USD 0.0325 per second | one 5 s clip: about USD 0.16 |
| song-minimax-music3-fal | minimax/music-3 | USD 0.002 per second | a 90 s song: about USD 0.18 |
| song-ace-step-fal | fal-ai/ace-step | USD 0.0002 per second | a 90 s song: about USD 0.02 (this is the older ACE-Step v1) |

fal's H3 at 480P outputs 832x480 (or 480x832) and crops any other shape, so make stills for
fal clips at 1664x960 or 960x1664. (Tested: an 832x1472 still lost 16 px at the top and the bottom.)

## Licences

Read the licence on each model's page before publishing or selling. What we checked:

- **Flux.2 Klein 9B**: FLUX Non-Commercial License (gated download on Hugging Face). Using
  it through fal or BFL's own API has its own terms.
- **Wan 2.2**: Apache 2.0, commercial use allowed (per ComfyUI's Wan 2.2 documentation).
- **MiniMax Music 3**: MiniMax-Music3 Community License; read it for the commercial terms
  and the credit it asks for.
- **H3 turbo LoRA**: trained by [larryvrh](https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora)
  (Apache 2.0); the file above is QrusherZA's ComfyUI conversion for the pruned H3 model.
- **ACE-Step 1.5, MiniMax H3, the Wan lightx2v LoRAs, the text encoders**: see each model card.
- **ComfyUI-fal-API**: Apache 2.0. fal and each model provider set the terms of API use.
