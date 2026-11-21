# Third-Party Notices

YTKACE / HH iOS tweak source is licensed under MIT. The following components, Android patch tools, and services have separate terms.

## ReVanced Extended Patches & Morphe Desktop (Android APK Injection)

The Android APK build (`Scripts/build-apk.sh`, `.github/workflows/build-apk.yml`, `Android/options.json`) injects unmodified patch bundles from [anddea/revanced-patches](https://github.com/anddea/revanced-patches) (originally forked from [inotia00](https://github.com/inotia00) and [ReVanced](https://github.com/ReVanced), with contributions ported from [Morphe](https://github.com/MorpheApp/morphe-patches)) using [Morphe Desktop](https://github.com/MorpheApp/morphe-desktop) and [Morphe Patcher](https://github.com/MorpheApp/morphe-patcher). Both projects are licensed under the **GNU General Public License v3.0 (GPLv3)** with Section 7 attribution and distinct-branding conditions:
- Original authors (**anddea**, **inotia00**, **ReVanced**, and **Morphe** contributors) and all in-app About/Credits notices are preserved unmodified.

## MicroG-RE / ReVanced GmsCore & YTDLnis

Companion Android packages downloaded by `.github/workflows/build-apk.yml` are unmodified upstream releases:
- [MorpheApp/MicroG-RE](https://github.com/MorpheApp/MicroG-RE) / [ReVanced/GmsCore](https://github.com/ReVanced/GmsCore) — Copyright microG Project Team, licensed under the **Apache License 2.0**.
- [deniscerri/ytdlnis](https://github.com/deniscerri/ytdlnis) — Copyright Denis Cerri, licensed under the **GNU General Public License v3.0 (GPLv3)**.

## FFmpeg

YTKACE statically links FFmpeg 8.1.2 for local media processing on iOS. It is built from the official release tarball by `Scripts/build-ffmpeg.sh`, without `--enable-gpl` and without `--enable-nonfree`, so the result is LGPL only. Licence texts ship in the repository at `Vendor/FFmpeg/COPYING.LGPLv2.1` and `COPYING.LGPLv3`. See https://ffmpeg.org/legal.html.

## SponsorBlock and DeArrow

SponsorBlock and DeArrow community data is provided by the SponsorBlock service under CC BY-NC-SA 4.0. See https://sponsor.ajay.app/. The shield image shipped in `YTKACE.bundle` is SponsorBlock's artwork, taken from the same site and used to mark the integration.

## SABR reference

The iOS download path implements YouTube's SABR streaming protocol. Protocol understanding came in part from reading [LuanRT/googlevideo](https://github.com/LuanRT/googlevideo), an MIT-licensed library implementing UMP and SABR. No code from that project is included.

## YTPlaybackFix

The playback error recovery in `Tweak/Features/Playback/PlaybackFixHooks.mm` is adapted from [YTPlaybackFix](https://github.com/Mark02-2012/YTPlaybackFix) by Mark02, used under the MIT licence.

MIT License, Copyright (c) 2026 Mark02.

## yt-dlp EJS challenge solver

`Resources/YTKACE.bundle/ejs/yt.solver.core.min.js` and `yt.solver.lib.min.js` are the JavaScript challenge solver from [yt-dlp/ejs](https://github.com/yt-dlp/ejs), release 0.8.0, released under the Unlicense (bundling `meriyah` under ISC License and `astring` under MIT License).

## TV & visionOS client identifiers

`Tweak/Features/Streaming/TVClient.mm`, `HLSPlayback.mm` and `DirectDownloader.mm` follow client identifier approaches published by [Morphe](https://github.com/MorpheApp/morphe-patches) and [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## YTLiquidGlass & LiquidLens

The Liquid Glass tab bar and top bar in `Tweak/Features/Navigation/TabBarHooks.mm` and `GlassChrome.mm` build on ideas from [YTLiquidGlass](https://github.com/UltraGeek0102/YTLiquidGlassEXTRA) by UltraGeek0102 (used with permission) and [Livsy90/LiquidLens](https://github.com/Livsy90/LiquidLens) (MIT licence).

## Apple frameworks

YTKACE uses UIKit, AVFoundation and SF Symbols supplied by iOS. SF Symbols artwork is requested at runtime and is not included as a redistributed asset pack.
