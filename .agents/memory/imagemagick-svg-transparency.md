---
name: ImageMagick SVG transparency
description: Avoid white fills when compositing SVG overlays over raster artwork with ImageMagick
---

When ImageMagick rasterizes an SVG overlay for compositing, set `-background none` before the SVG input. If applied after loading the SVG, transparent regions may be rendered white and obscure the underlying artwork.

**Why:** A social-preview overlay with a fading alpha gradient unexpectedly covered the background artwork in white until the SVG was loaded with a transparent background.

**How to apply:** Check the rasterized overlay's alpha channel before compositing it over a background image.