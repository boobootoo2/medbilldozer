#!/usr/bin/env python3
"""Generate audio files for splash screen narration.

Uses OpenAI Neural TTS with:
- Billy (male): echo voice (authoritative, clear)
- Billie (female): nova voice (warm, friendly)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from medbilldozer.ui.splash_screen import prepare_splash_audio

def main():
    """Generate all splash screen audio files."""
    print("🎙️ Generating Splash Screen Audio...")
    print()
    
    messages = [
        ("billie", "Hi! We're Billy and Billie—your guides to finding billing mistakes."),
        ("billy", "We scan medical bills, pharmacy receipts, dental claims, and insurance statements to uncover overcharges, duplicates, and missed reimbursements."),
        ("billie", "Ready to see how easy it is to double-check your bills?")
    ]
    
    print(f"Generating {len(messages)} audio files:")
    for idx, (character, text) in enumerate(messages, 1):
        voice = "echo" if character == "billy" else "nova"
        print(f"  {idx}. {character.title()} (voice: {voice})")
        print(f"     Text: {text[:60]}...")
    print()
    
    # Generate audio files
    prepare_splash_audio()
    
    print()
    print("✅ Splash screen audio generation complete!")
    print()
    
    # List generated files
    audio_dir = Path("audio")
    splash_files = sorted(audio_dir.glob("splash_*.mp3"))
    
    if splash_files:
        print("Generated files:")
        total_size = 0
        for f in splash_files:
            size = f.stat().st_size
            total_size += size
            print(f"  ✓ {f.name} ({size / 1024:.1f} KB)")
        print()
        print(f"Total size: {total_size / 1024:.1f} KB")
    else:
        print("⚠️ No audio files were generated. Check logs for errors.")
    
    print()
    print("Next steps:")
    print("  1. Test the splash screen: streamlit run app.py")
    print("  2. Stage audio files: git add audio/splash_*.mp3")
    print("  3. Commit: git commit -m 'Add splash screen audio narration'")

if __name__ == "__main__":
    main()
