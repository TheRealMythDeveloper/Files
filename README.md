# SONORA!!

**Reversible file storage through image and audio carriers.**

SONORA is a file-storage experiment that transforms regular files into actual PNG images or WAV audio files. The original file can later be recovered from its carrier with its data intact.

## Live Demo

**Website:** https://sonora-57c9.onrender.com

**API Documentation:** https://sonora-57c9.onrender.com/docs

## Features

- **File → PNG:** Encode files into valid PNG images.
- **File → WAV:** Encode files into valid WAV audio.
- **PNG → File:** Recover files from SONORA* PNG carriers.
- **WAV → File:** Recover files from SONORA* WAV carriers.
- **Integrity verification:** SHA-256 checks ensure recovered data matches the original.
- **Web interface:** Upload, process, and download files directly through the browser.
- **File support:** Supports arbitrary file types.
- **Size limit:** 25 MB per original file.

*Files originally transformed with Sonora.

## How It Works

SONORA packages a file's data together with its filename and SHA-256 hash.

That data is then encoded into a carrier:

- **PNG:** The packaged data is stored in pixel values.
- **WAV:** The packaged data is stored in audio samples.

When decoding, SONORA extracts the stored data, reconstructs the original file, and checks its SHA-256 hash to verify integrity. (All tests run have shown 100%!)

The carrier remains a valid image or audio file, while the embedded data can be recovered through SONORA.

## Usage

1. Open the [SONORA website](https://sonora-57c9.onrender.com).
2. Select an conversion operation.
3. Upload a file.
4. Convert the file.
5. Download the resulting image or wav file! (or more, using the decoding operation.)

### AI WAS USED.
I used AI to help me debug the connections between the API and the buttons. I had a lot of issues with it. 
(and code organization, so it looks pretty.)
Thats all! 