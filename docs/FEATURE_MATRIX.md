# Feature matrix

## Implemented (Injected Official YouTube — iOS IPA & Android APK)

| Area | iOS (`YTKACE.dylib` / IPA) | Android (`HH` Injected Stock YouTube APK) |
| --- | --- | --- |
| Core & Branding | Injected into official iOS YouTube; native `YouTube` name & icon + `HH` settings | Injected into official Android YouTube `21.13.164` (`com.hoanghuy.hh.youtube`); native `YouTube` name & icon + `HH` settings |
| Account Login | Native YouTube iOS sign-in | Native Google Account sign-in via `MicroG-RE` / `GmsCore` (`app.revanced.android.gms`) |
| Ads | Player ads, slots, placements, ad parameters, playback ad state, and companion ads | Video ads, feed ads, Shorts ads, merchandise banners, creator store shelves, and layout promos |
| SponsorBlock | Segment lookup, timeline markers, automatic skip, Ask mode, skipped HUD, sound, and haptic feedback | Full SponsorBlock integration: category controls, seekbar color markers, auto-skip, skip button, and segment submission |
| Dislikes & Titles | Native player integration | Return YouTube Dislike (RYD), Return YouTube Username, and DeArrow alternative thumbnails |
| Downloads | Built-in SABR adaptive video/audio downloader, FFmpeg MP4 remuxing, Shorts & playlist downloading, offline library, mini-player, backup & restore | In-player overlay Download button + native Download button & Playlist download hook (`YTDLnis` / `Seal` for MP4, 4K, MP3/M4A, Shorts & Playlists) |
| Queue | Play next / play last without Premium, reorder, swipe to remove, shuffle, loop, and clear | Unlocked Play next in queue without Premium (`Override Play next in queue`) + toolbar queue actions |
| Playback | Background playback, PiP, loop, speed controls, default speed, sleep timer, and custom double-tap duration | Background playback, PiP, video loop & seekbar segment loop, custom playback speeds, default speed & quality, audio pitch, Force HDR, custom double-tap seek, PoToken & stream spoofing |
| Appearance | OLED theme, Liquid Glass (iOS 26), and Premium logo | OLED pure-black (`#FF000000`) theme, Material You & custom themes, stock YouTube icon + 20+ selectable in-app icons |
| Tabs & Shorts | Hide and reorder tabs, Create-tab conversion, downloads tab, extra category tabs, startup selection, Shorts controls | Hide/reorder navigation tabs, hide Shorts/Create/Notifications buttons, custom startup page, Shorts component controls, wide search bar |
| Gestures | Volume, brightness, and hold-to-seek | Vertical volume & brightness swipe controls, customizable swipe zones, swipe-down fullscreen, and press-and-hold speed |
| Sharing & Misc | Copy Comment, iPadOS mode, native share sheet, forced LTR, age-gate flags, caption control, startup cache cleanup | System share sheet, tracking link sanitization, bypass URL redirects, remove viewer discretion dialog, Gemini summaries/search, Voice Over Translation, 25+ UI translations (`vi-rVN`, `en`, etc.) |
