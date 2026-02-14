# Quick Start Guide

## Generate Images (Recommended)

```bash
# Use default PIL provider (most realistic, free, instant)
python3 scripts/generate_clinical_images.py --all
```

That's it! This generates all 20 clinical benchmark images with realistic DICOM-style appearance.

## Run Benchmarks

```bash
# Test AI models on clinical error detection
python3 scripts/run_clinical_benchmarks.py --model all
```

## View Results

Open your Streamlit dashboard:
```bash
streamlit run pages/production_stability.py
```

Navigate to: **🩺 Clinical Error Detection** tab

---

## Why Use PIL (Default)?

✅ **Most realistic** - matches actual hospital DICOM viewers  
✅ **Free** - no API costs  
✅ **Instant** - generates in seconds  
✅ **Consistent** - same quality every time  

⚠️ **AI providers (OpenAI, etc.)** create artistic illustrations, not realistic diagnostic scans

## Other Options (If Needed)

### For Artistic/Presentation Images
```bash
python3 scripts/generate_clinical_images.py --all --provider openai
# ⚠️ Not recommended for benchmarks - creates artistic renderings
```

### For Specific Modalities
```bash
python3 scripts/generate_clinical_images.py --modality xray
python3 scripts/generate_clinical_images.py --modality mri
python3 scripts/generate_clinical_images.py --modality ct
```

### For Single Scenario
```bash
python3 scripts/generate_clinical_images.py --scenario scenario_001
```

## Understanding the Output

**20 scenarios generated:**
- Scenarios 001-010: Error cases (treatment doesn't match diagnosis)
- Scenarios 011-020: Correct cases (treatment matches diagnosis)

**Image files created in:**
`benchmarks/clinical_images/synthetic_images/`

**Benchmark results saved to:**
`benchmarks/clinical_images/results/`

## Need Help?

- 📖 Full documentation: `README.md`
- 🔍 Model capabilities: `MODEL_CAPABILITIES.md`
- 🎨 Image quality comparison: `IMAGE_QUALITY_COMPARISON.md`
- 📋 Implementation details: `IMPLEMENTATION_SUMMARY.md`

## Common Issues

**Q: Images look artistic/unrealistic?**
- A: You used an AI provider. Use PIL instead (default)

**Q: Slow generation?**
- A: You used an AI provider. PIL is instant

**Q: API key errors?**
- A: Don't need API keys for PIL (default provider)

**Q: MedGemma can't generate images?**
- A: Correct! MedGemma is text-only. Use PIL for images

**Q: Claude support?**
- A: Claude analyzes images, doesn't generate them

---

**Bottom Line**: Just run `python3 scripts/generate_clinical_images.py --all` and you're done! 🎉
