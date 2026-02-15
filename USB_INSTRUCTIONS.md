# VoicePerio - Portable USB Setup Guide

## For You (Building the USB)

### What You Need
- A Windows PC with Python 3.10+ and internet access
- A USB drive with at least 500MB free space

### Steps to Build

1. **Open a Command Prompt** in the VoicePerio project folder

2. **Run the build script:**
   ```
   scripts\build_portable_usb.bat
   ```

3. **Wait** for it to download Python Embeddable, install all dependencies, and copy the app files. This takes 5-10 minutes.

4. **Copy the output folder** `VoicePerio_Portable` to the USB drive. The folder will be ~400-500MB.

### What Gets Created

```
VoicePerio_Portable/
  VoicePerio_Launch.bat    <-- Client double-clicks this
  python/                  <-- Portable Python (no install needed)
  app/
    src/voiceperio/        <-- The application code
  models/
    vosk-model-small-en-us/ <-- Speech recognition model
```

---

## For Your Client (Using the USB)

### How to Use

1. **Plug in the USB drive**
2. **Open the VoicePerio_Portable folder** on the USB drive
3. **Double-click `VoicePerio_Launch.bat`**
4. VoicePerio will start -- no installation required!

### Important Notes

- **Do NOT close** the black command window that appears -- it runs VoicePerio
- **First launch** may take 10-20 seconds while the speech model loads
- The app works exactly the same as the installed version
- All settings are saved to the USB drive (portable)
- **Run as Administrator** may be needed for keystroke injection to work with Dentrix

### Troubleshooting

| Problem | Solution |
|---------|----------|
| "Blocked by IT policy" | Right-click the .bat file > Properties > Unblock |
| No microphone detected | Check Windows Sound Settings, allow mic access |
| Keystrokes not reaching Dentrix | Run the .bat file as Administrator |
| Antivirus warning | Add the USB folder to antivirus exclusions |
| Slow performance from USB | Copy VoicePerio_Portable folder to Desktop, run from there |

### If .bat Files Are Also Blocked

If the corporate environment also blocks .bat files, try renaming `VoicePerio_Launch.bat` to `VoicePerio_Launch.cmd` -- sometimes .cmd files have different policies.
