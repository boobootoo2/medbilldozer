# Splash Audio Narration - Quick Start

## 30-Second Setup

### Generate Audio Files

```bash
python3 scripts/generate_splash_audio.py
```

### Verify Files

```bash
ls -lh audio/splash_*.mp3
```

Expected output:
```
splash_billie_0.mp3  (81 KB)  - Billie's welcome
splash_billy_1.mp3   (166 KB) - Billy's explanation
splash_billie_2.mp3  (62 KB)  - Billie's call to action
```

### Test Splash Screen

```bash
streamlit run medBillDozer.py
```

1. Load homepage (splash appears)
2. Listen for Billie's welcome (female voice - nova)
3. Listen for Billy's explanation (male voice - echo)
4. Listen for Billie's call to action (female voice - nova)
5. Click "Get Started" to dismiss

## Voice Assignment

| Character | Voice | Gender | Tone | Lines |
|-----------|-------|--------|------|-------|
| **Billie** | `nova` | Female | Warm, friendly | Welcome + CTA |
| **Billy** | `echo` | Male | Clear, authoritative | Features explanation |

## Quick Reference

### Narration Script

1. **Billie** (nova): *"Hi! We're Billy and Billie—your guides to finding billing mistakes."*
2. **Billy** (echo): *"We scan medical bills, pharmacy receipts, dental claims, and insurance statements to uncover overcharges, duplicates, and missed reimbursements."*
3. **Billie** (nova): *"Ready to see how easy it is to double-check your bills?"*

### Audio Specs

- **Format**: MP3
- **Model**: OpenAI TTS-1 (Neural)
- **Total Size**: ~310 KB (3 files)
- **Cost**: ~$0.31 (one-time)
- **Caching**: Smart (skips existing files)

### Deployment

```bash
# Stage audio files
git add audio/splash_*.mp3

# Commit
git commit -m "Add splash screen dual-voice audio narration"

# Push
git push origin develop
```

## Troubleshooting

### Audio not playing?

1. Check browser console for errors
2. Verify files exist: `ls audio/splash_*.mp3`
3. Test individual files: `afplay audio/splash_billie_0.mp3` (macOS)

### Need to regenerate?

```bash
# Remove existing files
rm audio/splash_*.mp3

# Generate fresh copies
python3 scripts/generate_splash_audio.py
```

### Missing OpenAI API key?

```bash
# Set in environment
export OPENAI_API_KEY="sk-..."

# Or add to .env file
echo "OPENAI_API_KEY=sk-..." >> .env
```

## Full Documentation

See [SPLASH_AUDIO_NARRATION.md](SPLASH_AUDIO_NARRATION.md) for complete details.
