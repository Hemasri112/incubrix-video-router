# Open / Open-Weight Video Models — Source and Routing Notes

## 1. Scope

This document records research used by the IncuBrix video-generation routing system.

The five candidate video models evaluated for the routing registry are:

1. LTX-Video
2. Wan2.1
3. CogVideoX-2B
4. HunyuanVideo
5. Mochi-1

The purpose of this document is to distinguish:

- reported capabilities from official model sources
- our own measured execution results
- routing decisions made by the project

Reported values must not be presented as measurements from this project.

---

# 2. LTX-Video

## Official source

Repository:
https://github.com/Lightricks/LTX-Video

Model family:
LTX-Video

Model revision used for project execution:

`ltxv-2b-0.9.6-distilled-04-25`

## Reported capabilities

The official LTX-Video repository documents:

- text-to-video generation
- image-to-video generation
- video extension
- video-to-video workflows
- keyframe conditioning
- distilled 2B model
- 8-step recommended sampling for the 0.9.6 distilled model
- 15x faster inference than the corresponding non-distilled model
- improved prompt adherence, motion quality and fine details

The repository also reports that the 0.9.6 distilled model is intended for faster generation and can operate in real-time on an H100 under the documented configuration.

## Reported license information

The official LTX-Video repository is Apache-2.0 licensed.

The exact model/checkpoint license should be verified against the corresponding Hugging Face model card before making commercial-use claims for a specific checkpoint.

## Reported hardware / performance

The official repository describes the distilled 0.9.6 model as significantly faster than the non-distilled version and provides lower-VRAM options compared with larger LTX models.

These are reported values and are not treated as measurements from this project.

## Our measured execution

LTX-Video was actually executed by this project on a free Google Colab Tesla T4 accelerator.

Measured configuration:

- GPU: Tesla T4
- PyTorch: 2.11.0+cu128
- CUDA available: True
- Diffusers: 0.39.0
- Transformers: 4.51.3
- Hugging Face Hub: 0.36.2
- Model: LTX-Video 2B distilled
- Model revision: `ltxv-2b-0.9.6-distilled-04-25`
- Seed: 42
- Frames: 25
- Resolution: 512 x 768
- FPS: 8
- Inference steps: 8
- Measured generation runtime: approximately 19 seconds

The successful generated artifact was:

`ltx_baseline_test.mp4`

The generated artifact was saved to Google Drive as part of the reproducibility workflow.

## Execution notes

The official pipeline initially attempted to place the T5 text encoder on the GPU and ran out of CUDA memory on the T4.

A custom execution path was therefore used:

1. load T5 on CPU using bfloat16
2. encode positive and negative prompts
3. release T5 from memory
4. move the VAE and transformer to CUDA
5. construct the pipeline using precomputed prompt embeddings
6. generate the video
7. save the resulting MP4

This successfully completed generation on the T4.

The generated video contained visual artifacts and distorted text-like content. Therefore, generated text is not relied upon for final captions. Captions are generated and burned locally using FFmpeg.

## Routing relevance

LTX-Video is currently the strongest measured candidate in this project because it has:

- successful real accelerator execution
- measured runtime evidence
- a documented model revision
- deterministic seed recording
- text-to-video capability
- lower resource requirements than several larger candidates

---

# 3. Wan2.1

## Official source

Repository:
https://github.com/Wan-Video/Wan2.1

Model evaluated for routing:

`Wan2.1-T2V-1.3B`

## Reported capabilities

The official repository describes Wan2.1 as an open video foundation model supporting:

- text-to-video
- image-to-video
- video editing
- text-to-image
- video-to-audio

The T2V-1.3B model supports 480P generation.

The official repository recommends 480P for the 1.3B model because results at 720P are less stable due to limited training at that resolution.

## Reported license

The official repository is Apache-2.0 licensed.

## Reported hardware / performance

The official repository reports:

- approximately 8.19 GB VRAM for T2V-1.3B
- approximately 4 minutes for a 5-second 480P video on an RTX 4090 without optimization
- CPU offload and T5 CPU options are available to reduce GPU memory usage

These values are reported by the model authors and are not measurements from this project.

## Our execution status

Wan2.1 was investigated for execution on free Colab hardware.

The direct T5 loading path did not complete reliably within the available environment.

Therefore:

- no successful Wan2.1 generation is claimed
- no Wan2.1 runtime is recorded as a project measurement
- no Wan2.1 VRAM usage is recorded as a project measurement

## Routing relevance

Wan2.1 remains a strong candidate because of:

- Apache-2.0 licensing
- text-to-video support
- 1.3B parameter option
- relatively low reported VRAM requirement
- multiple video-generation tasks

However, this project does not claim a measured Wan2.1 execution.

---

# 4. CogVideoX-2B

## Official source

Repository:
https://github.com/zai-org/CogVideo

Model:

`CogVideoX-2B`

## Reported capabilities

The official repository documents CogVideoX-2B as an open video-generation model supporting text-to-video generation.

Reported specifications include:

- resolution: 720 x 480
- approximately 6 seconds of video
- 8 FPS
- default 49 frames
- English prompt support
- FP16/BF16/FP32 and quantized inference options

## Reported license

The CogVideo repository provides model-license information and the CogVideoX-2B model is released under Apache-2.0.

The project records the model license as reported rather than independently measured.

## Reported memory

The official repository reports the following for CogVideoX-2B:

- SAT BF16: approximately 26 GB
- Diffusers BF16: from approximately 5 GB under the documented optimizations
- Diffusers INT8 with TorchAO: from approximately 4.4 GB under the documented optimizations

The repository explicitly notes that these optimized memory figures were tested on A100/H100 hardware and may not directly represent memory usage on other GPUs.

## Reported inference speed

For the documented 50-step configuration, the official repository reports approximately:

- A100: 180 seconds
- H100: 90 seconds

These are author-reported values.

## Our execution status

CogVideoX-2B was investigated on free Colab hardware.

Attempts using quantized/offloaded configurations caused system-memory failures in the available environment.

Therefore:

- no successful CogVideoX-2B generation is claimed
- no project runtime measurement is recorded
- no project VRAM measurement is recorded

## Routing relevance

CogVideoX-2B is useful as a candidate because:

- it is relatively small compared with the 5B model
- it has documented quantized inference
- it supports text-to-video
- official documentation provides lower-memory Diffusers configurations

However, the project does not treat the reported memory numbers as local measurements.

---

# 5. HunyuanVideo

## Official source

Repository:
https://github.com/Tencent-Hunyuan/HunyuanVideo

## Reported capabilities

HunyuanVideo is a large video foundation model supporting text-conditioned video generation.

The official repository describes:

- text-to-video generation
- unified image/video generative architecture
- 3D VAE
- MLLM-based text encoding
- multiple aspect ratios
- 540P and 720P generation configurations

The official repository also reports its own human evaluation results against several closed-source systems.

Those evaluation results are treated as author-reported results, not measurements performed by this project.

## Reported license

HunyuanVideo uses the Tencent Hunyuan Community License.

This is NOT treated as equivalent to Apache-2.0.

The license has important territorial and usage restrictions.

In particular, the license excludes the European Union, United Kingdom and South Korea from its permitted territory.

Any commercial or redistribution decision involving HunyuanVideo must therefore be checked against the current license terms.

## Reported hardware

The official repository reports:

For 129 frames:

- 720 x 1280: approximately 60 GB GPU memory
- 544 x 960: approximately 45 GB GPU memory

The repository states that an NVIDIA CUDA GPU is required and that the model was tested on a single 80 GB GPU.

The repository recommends an 80 GB GPU for better generation quality.

## Our execution status

HunyuanVideo was not executed in this project because its reported hardware requirement is substantially above the available free T4 environment.

Therefore:

- no HunyuanVideo generation is claimed
- no project runtime measurement is recorded
- no project VRAM measurement is recorded

## Routing relevance

HunyuanVideo is a technically capable candidate but is unsuitable for the project's normal free-T4 execution path because of its very high reported memory requirement and more restrictive license.

It is therefore lower priority for a resource-constrained routing system.

---

# 6. Mochi-1

## Official source

Repository:
https://github.com/genmoai/mochi

Model:

`Mochi 1`

## Reported capabilities

The official repository describes Mochi 1 as an open video-generation model with:

- text-to-video generation
- strong motion quality
- strong prompt adherence in preliminary evaluation
- LoRA fine-tuning support
- CPU-offload inference support

The initial release generates videos at 480P.

The repository notes limitations including:

- occasional warping/distortion during extreme motion
- weaker performance for animated content
- optimization toward photorealistic styles

## Reported license

The official Mochi repository states that Mochi 1 is released under the Apache-2.0 license.

## Reported hardware

I reviewed it against the official sources. The structure is good, and the evidence boundary is strong. There is one important correction we should make before final submission.
1. Important: LTX-Video license
Your SOURCES.md currently says:
The official LTX-Video repository is Apache-2.0 licensed.

That statement is true for the repository, but your actual executed model is:
ltxv-2b-0.9.6-distilled-04-25

The exact model/checkpoint is not Apache-2.0. Its Hugging Face model page points to the LTXV Open Weights License, dated April 17, 2025. Hugging Face
The official LTX model documentation also explicitly links the 0.9.6-distilled-specific license separately from the repository license. Hugging Face
So your current wording is cautious, but we should make it even clearer.
Replace this section
## Reported license information

The official LTX-Video repository is Apache-2.0 licensed.

The exact model/checkpoint license should be verified against the corresponding Hugging Face model card before making commercial-use claims for a specific checkpoint.
with:
## Reported license information

The LTX-Video source repository is Apache-2.0 licensed.

However, the exact checkpoint executed in this project,
`ltxv-2b-0.9.6-distilled-04-25`, is governed by the
LTXV Open Weights License dated April 17, 2025.

Therefore, this project does NOT classify the executed LTX-Video
checkpoint as Apache-2.0.

The checkpoint license permits specified uses subject to its terms
and use-based restrictions. Commercial-use terms depend on the
license conditions and the status of the user/entity under those
terms.

The project therefore records the repository license and checkpoint
license separately.
## Our execution status

Mochi-1 was not executed in this project because the standard implementation's reported memory requirement is substantially above the available free T4 environment.

Therefore:

- no Mochi-1 generation is claimed
- no project runtime measurement is recorded
- no project VRAM measurement is recorded

## Routing relevance

Mochi-1 is technically attractive for photorealistic video generation, but its resource requirements make it unsuitable for the project's normal free-T4 route.

---

# 7. Model Comparison

| Model | Main capability | License | Reported resource profile | Project execution | Routing status |
|---|---|---|---|---|---|
| LTX-Video 2B distilled | T2V / I2V | Repository Apache-2.0; checkpoint license must be checked | Lower VRAM than larger LTX models | SUCCESS on T4 | Highest priority |
| Wan2.1 T2V-1.3B | T2V / I2V / editing | Apache-2.0 | ~8.19 GB VRAM reported | Not completed | Candidate |
| CogVideoX-2B | T2V | Apache-2.0 | ~5 GB minimum Diffusers BF16 reported with optimization | Not completed | Candidate |
| HunyuanVideo | T2V | Tencent Hunyuan Community License | ~45–60 GB minimum reported | Not attempted | Low priority |
| Mochi-1 | T2V | Apache-2.0 | ~60 GB reported for standard single-GPU implementation | Not attempted | Low priority |

---

# 8. Measured vs Reported Evidence

## Measured by this project

The following values are project measurements:

### LTX-Video

- GPU: Tesla T4
- Runtime: approximately 19 seconds
- Resolution: 512 x 768
- Frames: 25
- FPS: 8
- Inference steps: 8
- Seed: 42
- Successful MP4 generation: Yes

### Local pipeline benchmark

The routing/assembly benchmark was executed on 10 varied briefs.

Measured result:

- total briefs: 10
- successful renders: 10
- render success rate: 100%
- route accuracy: 100%
- average latency: approximately 2.10 seconds

These 10 benchmark latency values measure the local routing + CPU workflow assembly pipeline.

They are NOT ten generative-video-model inference measurements.

All ten benchmark outputs used the CPU workflow assembly path.

Therefore these benchmark results must not be described as ten LTX/Wan/CogVideoX/Hunyuan/Mochi inference runs.

---

# 9. Routing Decision

The project router considers:

1. text-to-video capability
2. requested duration compatibility
3. requested aspect-ratio compatibility
4. local execution availability
5. measured runtime evidence
6. registry priority
7. fallback availability

A model with measured execution evidence receives stronger routing preference than a model with only reported capability information.

The router does not treat reported runtime or VRAM values as project measurements.

When no compatible model can be executed, the pipeline uses a local CPU/FFmpeg workflow assembly fallback.

---

# 10. Fallback Strategy

The system distinguishes between:

### Model generation

A real video-generation model produces the visual artifact.

### CPU workflow assembly

The local pipeline creates a deterministic draft using:

- FFmpeg
- workflow-specific visual treatments
- scene planning
- captions
- timeline metadata
- validation
- manifest generation

CPU workflow assembly is a fallback and must not be described as AI-generated video.

---

# 11. Reproducibility

For model-generated outputs, the project records:

- model name
- model revision
- prompt
- seed
- output path
- runtime when measured
- generation method
- model license information

For assembled outputs, the project records:

- workflow
- scene plan
- timeline
- captions
- output video
- validation result
- generation method
- manifest

The project uses deterministic seeds where supported.

---

# 12. Source Classification

Each source is classified as:

- `official_repository`
- `official_model_card`
- `official_technical_report`
- `measured_project_result`

Official sources provide reported model facts.

Project measurements are generated only from executions performed by this project.

No third-party benchmark is represented as a project measurement.

---

# 13. Primary Sources

## LTX-Video

Official repository:
https://github.com/Lightricks/LTX-Video

Official Hugging Face organization/model resources:
https://huggingface.co/Lightricks

## Wan2.1

Official repository:
https://github.com/Wan-Video/Wan2.1

Official Hugging Face organization:
https://huggingface.co/Wan-AI

## CogVideoX

Official repository:
https://github.com/zai-org/CogVideo

Official Hugging Face organization:
https://huggingface.co/THUDM

## HunyuanVideo

Official repository:
https://github.com/Tencent-Hunyuan/HunyuanVideo

Official Hugging Face organization:
https://huggingface.co/tencent

## Mochi-1

Official repository:
https://github.com/genmoai/mochi

Official Genmo model resources:
https://huggingface.co/genmo

---

# 14. Important Evidence Boundary

The five-model research satisfies the research/documentation component of the routing system.

However, only LTX-Video has been successfully executed by this project on the available free accelerator environment.

The other four models are documented candidates based on official sources and observed installation/execution constraints.

The project therefore does NOT claim successful execution of all five models.

This distinction is intentional and is required for reproducible engineering evidence.