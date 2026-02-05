#!/usr/bin/env python3
"""Generate audio narration files for guided tour.

Supports multiple TTS engines:
- OpenAI Neural TTS (recommended for production)
- pyttsx3 (local, offline)
- Text export for manual recording

For production, use OpenAI TTS for highest quality natural-sounding voices.
"""

import sys
from pathlib import Path

# Add parent directory to path to import tour module
sys.path.insert(0, str(Path(__file__).parent.parent))

from medbilldozer.ui.guided_tour import TOUR_STEPS


def generate_audio_openai():
    """Generate audio files using OpenAI Neural TTS (highest quality)."""
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ OpenAI library not installed. Install with: pip install openai")
        return

    # Initialize client (reads OPENAI_API_KEY from environment)
    try:
        client = OpenAI()
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        print("\n💡 Make sure OPENAI_API_KEY is set:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return

    # Create audio directory
    audio_dir = Path(__file__).parent.parent / "audio"
    audio_dir.mkdir(exist_ok=True)
    
    print("🎙️  Generating audio narration with OpenAI Neural TTS...\n")
    print("Voice: alloy (warm, neutral)")
    print("Model: tts-1 (optimized for speed)\n")
    
    for step in TOUR_STEPS:
        output_file = audio_dir / f"tour_step_{step.id}.mp3"
        
        # Skip if already exists
        if output_file.exists():
            print(f"⏭️  Step {step.id}: Already exists, skipping")
            continue
        
        print(f"🎤 Step {step.id}: {step.title}")
        print(f"   Text: {step.narration[:60]}...")
        
        try:
            response = client.audio.speech.create(
                model="tts-1",  # Use tts-1-hd for highest quality (slower)
                voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
                input=step.narration,
                speed=1.0
            )
            
            output_file.write_bytes(response.read())
            print(f"   ✅ Saved: {output_file.name} ({output_file.stat().st_size // 1024} KB)")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Audio generation complete!")
    print(f"📁 Files saved to: {audio_dir}")
    print(f"\n💰 Estimated cost: ${len(TOUR_STEPS) * 0.015:.3f}")
    print(f"   (OpenAI TTS pricing: ~$0.015 per 1000 characters)")


def generate_audio_files():
    """Generate audio files using pyttsx3 (local TTS)."""
    try:
        import pyttsx3
    except ImportError:
        print("❌ pyttsx3 not installed. Install with: pip install pyttsx3")
        print("\nAlternatively, use cloud TTS services for better quality:")
        print("  - Google Cloud Text-to-Speech")
        print("  - Amazon Polly")
        print("  - ElevenLabs")
        return

    # Initialize TTS engine
    engine = pyttsx3.init()
    
    # Configure voice properties
    voices = engine.getProperty('voices')
    # Try to use a more natural voice if available
    for voice in voices:
        if 'english' in voice.name.lower() or 'en_' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    
    engine.setProperty('rate', 150)  # Speed (words per minute)
    engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    
    # Create audio directory
    audio_dir = Path(__file__).parent.parent / "audio"
    audio_dir.mkdir(exist_ok=True)
    
    print(f"🎙️  Generating audio narration files...\n")
    
    for step in TOUR_STEPS:
        output_file = audio_dir / f"tour_step_{step.id}.mp3"
        
        # pyttsx3 can't directly save as MP3, so we save as WAV first
        wav_file = audio_dir / f"tour_step_{step.id}.wav"
        
        print(f"📝 Step {step.id}: {step.title}")
        print(f"   Text: {step.narration[:60]}...")
        
        try:
            engine.save_to_file(step.narration, str(wav_file))
            engine.runAndWait()
            print(f"   ✅ Saved: {wav_file.name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Audio generation complete!")
    print(f"📁 Files saved to: {audio_dir}")
    print(f"\n⚠️  Note: Files are in WAV format.")
    print(f"   Convert to MP3 for better web performance:")
    print(f"   ffmpeg -i audio/tour_step_1.wav -codec:a libmp3lame -qscale:a 2 audio/tour_step_1.mp3")


def print_narration_text():
    """Print narration text for manual recording or cloud TTS."""
    print("📋 Tour Narration Text\n")
    print("=" * 60)
    
    for step in TOUR_STEPS:
        print(f"\nStep {step.id}: {step.title}")
        print("-" * 60)
        print(step.narration)
        print(f"\nSuggested filename: tour_step_{step.id}.mp3")
        print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate guided tour audio narration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate using OpenAI Neural TTS (recommended)
  python scripts/generate_tour_audio.py --openai
  
  # Generate using local TTS (offline, lower quality)
  python scripts/generate_tour_audio.py --local
  
  # Print narration text for manual recording
  python scripts/generate_tour_audio.py --print-text
"""
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--openai",
        action="store_true",
        help="Generate audio using OpenAI Neural TTS (highest quality, requires API key)"
    )
    group.add_argument(
        "--local",
        action="store_true",
        help="Generate audio using local pyttsx3 TTS (offline, lower quality)"
    )
    group.add_argument(
        "--print-text",
        action="store_true",
        help="Print narration text for manual recording or cloud TTS services"
    )
    
    args = parser.parse_args()
    
    if args.openai:
        generate_audio_openai()
    elif args.local:
        generate_audio_files()
    elif args.print_text:
        print_narration_text()
    else:
        # Default: show help
        print("🎙️  MedBillDozer Tour Audio Generator\n")
        print("Choose a generation method:\n")
        print("  --openai      ⭐ Recommended: Neural TTS (requires OpenAI API key)")
        print("  --local       💻 Local TTS (offline, lower quality)")
        print("  --print-text  📋 Export text for manual recording\n")
        print("Run with --help for more details")
