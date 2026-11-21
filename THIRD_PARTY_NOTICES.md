# Third-Party Notices

YTKACE / HH iOS tweak source is licensed under MIT. The following components, Android base clients, patch tools, and services have separate terms.

## PipePipe & NewPipe (Android All-in-One APK)

The default standalone single-file Android build (`HH_1.1.1_YouTube.apk`, built by `Scripts/build-apk.sh` and `Tools/customize_pipepipe.py`) is customized from [PipePipe](https://github.com/InfinityLoop1308/PipePipe) v5.6.0 by InfinityLoop1308 (forked from [NewPipe](https://github.com/TeamNewPipe/NewPipe) by TeamNewPipe). PipePipe and NewPipe are free and open-source software licensed under the **GNU General Public License v3.0 (GPLv3)** (https://www.gnu.org/licenses/gpl-3.0.html). Modifications performed by `Tools/customize_pipepipe.py` (package namespace `com.hoanghuy.hh`, `HH` launcher branding, OLED black default theme, 1080p default resolution, and disabling upstream auto-update prompts) are distributed in source form in this repository under GPLv3 compatibility, preserving all upstream in-app About/License credits.

## APKEditor & uber-apk-signer

Android resource decoding/rebuilding and APK v1/v2/v3 signing in `Scripts/build-apk.sh` use:
- [REAndroid/APKEditor](https://github.com/REAndroid/APKEditor) — licensed under the **Apache License 2.0**.
- [patrickfav/uber-apk-signer](https://github.com/patrickfav/uber-apk-signer) — licensed under the **Apache License 2.0**.

## ReVanced Extended Patches & Morphe Desktop (Optional RVX Edition)

The optional `rvx` Android build mode (`Android/options.json`, `HH_APK_EDITION=rvx`) applies unmodified patch bundles from [anddea/revanced-patches](https://github.com/anddea/revanced-patches) using [MorpheApp/morphe-desktop](https://github.com/MorpheApp/morphe-desktop), both licensed under the **GNU General Public License v3.0 (GPLv3)** with Section 7 attribution terms. Original authors (**anddea**, **inotia00**, **ReVanced**, and **Morphe** contributors) and in-app credits are preserved unmodified.

## FFmpeg

YTKACE statically links FFmpeg 8.1.2 for local media processing on iOS. It is built from the official release tarball by `Scripts/build-ffmpeg.sh`, without `--enable-gpl` and without `--enable-nonfree`, so the result is LGPL only. Licence texts ship in the repository at `Vendor/FFmpeg/COPYING.LGPLv2.1` and `COPYING.LGPLv3`. See https://ffmpeg.org/legal.html.

## SponsorBlock and DeArrow

SponsorBlock and DeArrow community data is provided by the SponsorBlock service under CC BY-NC-SA 4.0. See https://sponsor.ajay.app/. The shield image shipped in `YTKACE.bundle` is SponsorBlock's artwork, taken from the same site and used to mark the integration.

## SABR reference

The iOS download path implements YouTube's SABR streaming protocol. It was written for YTKACE, developed against an iPad on iOS 16. Protocol understanding came in part from reading [LuanRT/googlevideo](https://github.com/LuanRT/googlevideo), an MIT-licensed library implementing UMP and SABR. No code from that project is included.

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
