# Feature matrix

## Implemented (iOS IPA & Android Single-File APK)

| Area | iOS (`YTKACE.dylib` / IPA) | Android (`HH_1.1.1_YouTube.apk` — All-in-One) |
| --- | --- | --- |
| Core & Install | Always-on local runtime; single sideloadable IPA | Standalone single APK (`com.hoanghuy.hh`), installs directly without root, GmsCore, or companion apps |
| Account Login | Native YouTube iOS sign-in | Built-in WebView YouTube account login (`Settings → Account → Log in to YouTube`) with cookie sync & age-restricted video access |
| Ads | Player ads, slots, placements, ad parameters, playback ad state, and companion ads | 100% ad-free video streams, feeds, search results, and comments |
| SponsorBlock | Segment lookup, timeline markers, automatic skip, Ask mode, skipped HUD, sound, and haptic feedback | Built-in SponsorBlock (enabled by default): category controls, seekbar color markers, auto-skip, manual skip button, and alerts |
| Dislikes & Titles | Native player integration | Built-in Return YouTube Dislike (RYD) and DeArrow alternative thumbnails & titles |
| Downloads | Built-in SABR adaptive video/audio downloader, FFmpeg MP4 remuxing, Shorts & playlist downloading, offline library, mini-player, backup & restore | Built-in multi-threaded Video (up to 4K `2160p`), Audio (`M4A`/`Opus`), Shorts, and batch Playlist/Channel downloader with pause/resume manager |
| Queue | Play next / play last without Premium, reorder, swipe to remove, shuffle, loop, and clear | Built-in Play Queue without Premium: Play next, Enqueue, drag-to-reorder, remove, shuffle, repeat/loop, and background queue |
| Playback | Background playback, PiP, loop, speed controls, default speed, sleep timer, and custom double-tap duration | Background audio playback, floating Popup / PiP player, sleep timer, custom speed & pitch controls, 1080p default / 4K support, Android Auto support |
| Appearance | OLED theme, Liquid Glass (iOS 26), and Premium logo | OLED pure-black (`#000000`) theme enabled by default, custom `HH` crimson/OLED launcher icon, grid/list layout controls |
| Tabs & Filters | Hide and reorder tabs, Create-tab conversion, downloads tab, extra category tabs, startup selection | Customizable main page tabs, channel tabs, Shorts hiding, and keyword/channel feed & comment filters |
| Gestures | Volume, brightness, and hold-to-seek | Vertical volume & brightness swipe gestures, swipe fullscreen, double-tap seek, and long-press speed |
| Localization | 15 languages (`en`, `vi`, etc.) + searchable settings | 60+ languages including English & Vietnamese (`Tiếng Việt`) + searchable settings & backup/restore |
