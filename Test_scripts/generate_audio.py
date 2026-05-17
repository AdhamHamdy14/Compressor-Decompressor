import wave

# Generate 5 seconds of perfect digital silence
with wave.open("./tests/perfect_silence.wav", "w") as w:
    w.setnchannels(1)       # Mono
    w.setsampwidth(1)       # 8-bit audio (1 byte per sample)
    w.setframerate(8000)    # 8000 samples per second

    # 8-bit WAV uses 128 as "silence" (midpoint)
    # 5 seconds * 8000 samples = 40,000 bytes of exactly '128'
    w.writeframes(bytes([128] * 40000))

print("✅ Created perfect_silence.wav (40 KB)")
