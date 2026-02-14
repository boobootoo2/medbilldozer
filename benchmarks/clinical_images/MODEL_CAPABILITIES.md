# AI Model Capabilities Reference

Quick reference for which AI models can generate images vs analyze images in the clinical error detection benchmarks.

## Image Generation (generate_clinical_images.py)

Models that can **CREATE** synthetic medical images:

### ✅ Supported Image Generation Providers

| Provider | Cost/Image | Quality | Realism | Setup Required |
|----------|-----------|---------|---------|----------------|
| **PIL/Pillow** | Free | Basic | ⭐⭐⭐⭐⭐ Most Realistic | None (default) |
| **OpenAI DALL-E 3** | ~$0.04 | High | ⭐⭐ Artistic/Illustrative | OPENAI_API_KEY |
| **Stability AI SDXL** | ~$0.03 | Good | ⭐⭐⭐ Variable | STABILITY_API_KEY |
| **Replicate SDXL** | ~$0.01 | Good | ⭐⭐⭐ Variable | REPLICATE_API_TOKEN |
| **Google Imagen** | ~$0.02 | Good | ⭐⭐⭐ Variable | GOOGLE_CLOUD_PROJECT + auth |

**⚠️ Important Note**: AI image generators (DALL-E, Stable Diffusion, Imagen) often produce artistic/illustrative medical images rather than realistic diagnostic scans. For authentic-looking clinical diagnostic images, **PIL/Pillow** (default) produces the most realistic DICOM-style medical imaging appearance.

### ❌ Cannot Generate Images

| Model | Reason | What It CAN Do |
|-------|--------|----------------|
| **Claude** | Text/vision analysis model only | Analyze images in benchmarks |
| **MedGemma** | Text-only medical language model | Analyze clinical text |
| **Gemini Vision** | Vision analysis, not generation | Analyze images in benchmarks |
| **GPT-4 Vision** | Vision analysis, not generation | Analyze images in benchmarks |

## Image Analysis (run_clinical_benchmarks.py)

Models that can **ANALYZE** medical images to detect clinical errors:

### ✅ Supported Analysis Models

| Model | Type | Setup Required |
|-------|------|----------------|
| **GPT-4o-mini** | Vision + Text | OPENAI_API_KEY |
| **Gemini 1.5 Flash** | Vision + Text | GOOGLE_API_KEY |
| **Claude 3.5 Sonnet** | Vision + Text | ANTHROPIC_API_KEY |
| **Claude 3 Haiku** | Vision + Text (faster) | ANTHROPIC_API_KEY |

### 🔄 Coming Soon

| Model | Status | Notes |
|-------|--------|-------|
| **MedGemma + Vision** | Pending Google API | Text-only currently |
| **Gemini Pro Vision** | Available | Similar to Flash |

## Usage Examples

### Generate Images

```bash
# Default (free, fast, basic quality)
python3 scripts/generate_clinical_images.py --all

# High quality with OpenAI
python3 scripts/generate_clinical_images.py --all --provider openai

# Cost-effective with Replicate
python3 scripts/generate_clinical_images.py --all --provider replicate

# Google Imagen (requires GCP setup)
python3 scripts/generate_clinical_images.py --all --provider google-imagen
```

### Analyze Images (Detect Clinical Errors)

```bash
# Test with OpenAI GPT-4o-mini
python3 scripts/run_clinical_benchmarks.py --model gpt-4o-mini

# Test with Google Gemini
python3 scripts/run_clinical_benchmarks.py --model gemini-1.5-flash

# Test with Claude (when added)
python3 scripts/run_clinical_benchmarks.py --model claude-3-haiku

# Test all available models
python3 scripts/run_clinical_benchmarks.py --model all
```

## Recommended Workflow

### For Development/Testing (Recommended)
1. **Generate images**: Use `--provider pil` (free, instant, most realistic)
2. **Test benchmarks**: Use `--model all` to test available models

### For Realistic Diagnostic Images (Recommended)
1. **Generate images**: Use `--provider pil` (default) - creates authentic DICOM-style medical imaging
2. **Run benchmarks**: Test multiple models for comparison
3. **Compare results**: Evaluate accuracy, precision, recall, F1

### For Artistic/High-Resolution Images
1. **Generate images**: Use `--provider openai` or `--provider google-imagen`
   - ⚠️ **Warning**: May produce artistic renderings rather than realistic diagnostic scans
   - Better for presentations/illustrations than benchmark testing
2. **Run benchmarks**: Results may differ from real clinical imaging

### For Budget-Conscious Use
1. **Generate images**: Use `--provider pil` (free AND most realistic)
2. **Run benchmarks**: Use single model or baseline

## Cost Comparison

### Generating 20 Images

| Provider | Total Cost | Per Image |
|----------|-----------|-----------|
| PIL | $0.00 | Free |
| Replicate | ~$0.20 | $0.01 |
| Google Imagen | ~$0.40 | $0.02 |
| Stability AI | ~$0.60 | $0.03 |
| OpenAI DALL-E | ~$0.80 | $0.04 |

### Running Benchmarks (20 scenarios)

| Model | Total Cost | Per Scenario |
|-------|-----------|--------------|
| Baseline (Mock) | $0.00 | Free |
| GPT-4o-mini | ~$0.40 | ~$0.02 |
| Gemini Flash | ~$0.20 | ~$0.01 |
| Claude Haiku | ~$0.50 | ~$0.025 |

## API Key Setup

### OpenAI (DALL-E 3 + GPT-4o-mini)
```bash
# Add to .env file
OPENAI_API_KEY=sk-...
```

### Google Cloud (Imagen + Gemini)
```bash
# Add to .env file
GOOGLE_API_KEY=...
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Or use gcloud CLI
gcloud auth application-default login
```

### Anthropic (Claude - for analysis only)
```bash
# Add to .env file
ANTHROPIC_API_KEY=sk-ant-...
```

### Stability AI (Image generation)
```bash
# Add to .env file
STABILITY_API_KEY=sk-...
```

### Replicate (Image generation)
```bash
# Add to .env file
REPLICATE_API_TOKEN=r8_...
```

## Key Takeaways

✅ **For Image Generation**:
- Use **PIL** for realistic diagnostic imaging (recommended for benchmarks)
- Use **PIL** for free/fast development
- Use **OpenAI DALL-E** for artistic/presentation images (⚠️ not realistic diagnostic scans)
- Use **Replicate** for budget AI generation (⚠️ variable realism)

✅ **For Image Analysis**:
- Use **GPT-4o-mini** for balanced performance
- Use **Gemini Flash** for lower cost
- Use **Claude** for detailed analysis

❌ **Cannot Generate Images**:
- Claude (text/vision analysis only)
- MedGemma (text-only)
- Any vision-only models

🎯 **Best Practice**:
- Generate once with quality provider
- Test multiple analysis models
- Compare results for research

## Questions?

- **Q: Can I use MedGemma to generate images?**
  - A: No, MedGemma is a text-only model for medical reasoning

- **Q: Can Claude generate images?**
  - A: No, but Claude can analyze images in `run_clinical_benchmarks.py`

- **Q: Why do OpenAI images look unrealistic/artistic?**
  - A: DALL-E and other AI image generators create artistic renderings, not true diagnostic scans
  - A: For realistic DICOM-style medical imaging, use PIL (default provider)

- **Q: What's the best option for realistic diagnostic images?**
  - A: **PIL (default)** - creates authentic-looking DICOM-style clinical scans
  - A: Free, instant, and most realistic for benchmark testing

- **Q: What's the best free option?**
  - A: Use PIL for image generation (free, local, AND most realistic)
  - A: Use baseline mock for initial testing (free)

- **Q: What's the best quality for presentations?**
  - A: OpenAI DALL-E 3 for high-resolution artistic medical images
  - A: ⚠️ Not recommended for diagnostic realism benchmarks

- **Q: What's the best value?**
  - A: PIL for free realistic imaging (recommended)
  - A: Replicate for budget AI generation if you need AI ($0.01/image)
  - A: Gemini Flash for analysis (~$0.01/scenario)
