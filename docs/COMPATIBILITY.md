# Compatibility

## Android baseline (All-in-One Single APK)

`HH_1.1.1_YouTube.apk` (`com.hoanghuy.hh`) is a standalone single-file Android client customized from [PipePipe](https://github.com/InfinityLoop1308/PipePipe) `5.6.0`:
- **Minimum OS:** Android 7.0 (API 24) and newer.
- **Architectures:** `arm64-v8a` (default) and `armeabi-v7a`.
- **Single-File Installation:** Installs directly as a single `.apk` without root, without `GmsCore` / `MicroG`, and without external downloader apps.
- **Built-in Capabilities:** Ad-free streaming, built-in multi-threaded Video/Audio/Shorts/Playlist downloader, SponsorBlock (on by default), Return YouTube Dislike, DeArrow, background & popup PiP playback, play queue, direct WebView YouTube login, and OLED pure-black theme (on by default).
- **Optional RVX Edition:** Setting `HH_APK_EDITION=rvx` in `Scripts/build-apk.sh` or `.github/workflows/build-apk.yml` builds the stock-YouTube `21.13.164` + `anddea/revanced-patches` `4.3.0` variant (`com.hoanghuy.hh.youtube`, which requires `GmsCore` on non-root Android).

## iOS baseline

YouTube 21.26.4+ has a minimum deployment version of iOS 16.0 and links
AppIntents (YouTube 21.39.4 requires iOS 17.0). Changing `Info.plist` alone
cannot make it an iOS 15 application.

The `YTKACE.dylib` tweak itself targets iOS 15 (`arm64`) and can be repacked into an older
YouTube baseline that also targets iOS 15.

The same repacked IPA can be installed through TrollStore, AppSync-compatible
installers, or re-signed by a developer-certificate sideloader. No runtime
injection environment is required.
