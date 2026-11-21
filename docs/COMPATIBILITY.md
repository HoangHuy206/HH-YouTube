# Compatibility

## Android baseline (Injected Stock YouTube APK)

`HH_1.1.1_YouTube_21.13.164.apk` (`com.hoanghuy.hh.youtube`) is built directly from the official Google YouTube `21.13.164` Android baseline (minimum SDK Android 8.0 / API 26) using `anddea/revanced-patches` `v4.3.0` and `MorpheApp/morphe-desktop` `v2.3.0`:
- **Native UI & Branding:** Retains 100% of the official YouTube application UI, launcher name (`YouTube`), and stock YouTube launcher icon while exposing the **`HH`** configuration menu inside YouTube Settings.
- **Architectures:** `arm64-v8a` and `armeabi-v7a` by default.
- **Side-by-Side Installation:** Uses package identifier `com.hoanghuy.hh.youtube` so it installs cleanly alongside pre-installed system YouTube without root.
- **Google Sign-In (Non-Root):** Uses `GmsCore support` targeting `app.revanced.android.gms` (`MicroG-RE` 7.3.1 or `ReVanced GmsCore`). Install `MicroG-RE` once prior to launching YouTube.
- **Direct Media Downloads:** `Hook download actions` and `Overlay buttons` connect the player and playlist download buttons directly to `YTDLnis` or `Seal` for MP4 (up to 4K), MP3/M4A, Shorts, and Playlist downloads.

## iOS baseline (Injected Stock YouTube IPA)

YouTube 21.26.4+ has a minimum deployment version of iOS 16.0 and links
AppIntents (YouTube 21.39.4 requires iOS 17.0). Changing `Info.plist` alone
cannot make it an iOS 15 application.

The `YTKACE.dylib` tweak itself targets iOS 15 (`arm64`) and can be repacked into an older
YouTube baseline that also targets iOS 15.

The same repacked IPA can be installed through TrollStore, AppSync-compatible
installers, or re-signed by a developer-certificate sideloader. No runtime
injection environment is required.
