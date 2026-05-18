# Image Generation Prompts — Prompt Optimization Frameworks vs AI Agents

A 4-image visual story. Two characters throughout: **you** (a male engineer) and **your small cute robot companion**. You're guiding it through your journey.

**Style:** Retro-futurist isometric illustration. Clean linework, subtle halftone texture, warm earth-tone palette. Isometric perspective throughout for visual consistency.

**Palette:** Terracotta (#B5553E), sage green (#7A8B6F), golden sand (#D4A54A), warm parchment (#EDE4D3), deep umber (#3E2723). No mint, no teal, no mauve.

**The Robot Character (original design — NOT R2D2, NOT BB-8):**
- **Size:** Knee-height to the human, small and compact
- **Shape:** A boxy body with softly rounded corners — like a vintage Polaroid camera or a small retro TV on wheels. Flat front face, not cylindrical or spherical
- **Eye:** One large round lens on the front face that glows warm gold, like a camera aperture
- **Arms:** Two small articulated mechanical arms that fold out from the sides
- **Mobility:** Rolls on a set of small chunky rubber treads (not legs, not a ball)
- **Antenna:** A short bent wire antenna on top that tilts to show emotion
- **Material:** Brushed copper and cream-colored panels with visible rivets
- **Personality:** Eager, loyal, curious — expresses emotion through its lens brightness, antenna tilt, and arm gestures

---

## 1. THE STRUGGLE (Hero / Title)

**Story:** You've brought your little robot into a massive, overwhelming optimization factory. You're pointing at the complicated machinery, trying to explain how it works. The robot looks up at the towering machine, its lens dim with confusion, antenna drooping.

```
Retro-futurist isometric illustration, clean linework, subtle halftone grain. Isometric view of a vast retro optimization factory interior. A young male engineer with light brown skin and black hair in work clothes stands next to a small boxy robot companion — the robot is knee-height with a flat front face featuring one large round camera-lens eye, two small folding arms, chunky rubber treads, a short bent antenna on top, and a body of brushed copper and cream panels with visible rivets. The engineer gestures up at a towering wall of machinery — brass pipes, spinning dials, vacuum tubes, reel-to-reel tapes, tangled cables. The little robot's antenna droops sideways, its lens dim, looking up at the overwhelming machine. Printouts with contradictory numbers litter the floor around them. The machine is imposing, the two figures are small against it. Warm palette of terracotta, sage green, golden sand, parchment cream, deep umber. No teal, no mint, no mauve. Golden hour light from tall windows. 16:9.
```

---

## 2. THE IDEA (The Moment It Clicked)

**Story:** You've left the factory behind. You're sitting on a bench outside in warm sunlight, writing your process in a notebook. The little robot sits on the ground next to the bench, leaning in, its lens glowing brighter as it watches you write.

```
Retro-futurist isometric illustration, clean linework, subtle halftone grain. Isometric view of a peaceful outdoor scene — a timber bench under a eucalyptus tree, warm golden afternoon light. A young male engineer with light brown skin and black hair sits on the bench writing intently in a leather notebook — visible handwritten notes and simple diagrams on the pages. On the ground next to the bench, the same small boxy robot companion (knee-height, one large round lens eye, brushed copper and cream body, chunky treads, bent antenna) leans in toward the notebook, its lens glowing warm gold with curiosity, antenna perked up. In the far background, barely visible, the dark silhouette of the optimization factory they left behind. The mood is calm, thoughtful, a breakthrough happening quietly. Warm palette of terracotta, sage green, golden sand, parchment cream, deep umber. No teal, no mint, no mauve. 16:9.
```

---

## 3. THE HANDOFF (What Actually Worked: Agent Skills)

**Story:** You've finished writing the manual. You kneel down and hand the open notebook to the little robot. It reaches out with both small arms to receive it, its lens glowing bright, antenna standing straight up — it understands.

```
Retro-futurist isometric illustration, clean linework, subtle halftone grain. Isometric view of a warm intimate scene. A young male engineer with light brown skin and black hair kneels on one knee, handing an open leather notebook down to the same small boxy robot companion. The robot reaches out with both small articulated arms to receive it carefully, its large round lens eye glowing bright warm gold, its antenna standing straight up with eagerness. The notebook shows visible handwritten pages with neat process steps. The setting is a simple, warmly-lit workshop with timber floors, a workbench in the background, sunlight streaming through a window. The mood is trust and partnership. Warm palette of terracotta, sage green, golden sand, parchment cream, deep umber. No teal, no mint, no mauve. 16:9.
```

---

## 4. AT SCALE (Real Results / The Broader Pattern)

**Story:** The little robot took your manual and ran with it. Now copies of it work across rows of simple workbenches, each with the notebook open, each methodically doing the work. You stand in the foreground watching with quiet pride. No complex machinery in sight.

```
Retro-futurist isometric illustration, clean linework, subtle halftone grain. Isometric wide view of a spacious sunlit workshop. Rows of simple timber workbenches stretch into the background. At each bench, a copy of the same small boxy robot companion works methodically — each has the leather notebook open beside it, each uses simple tools with its small articulated arms, each examines documents under warm desk lamps, all lenses glowing bright. No complex machinery anywhere — just clean, simple workstations. In the foreground corner, the young male engineer with light brown skin and black hair stands watching with arms folded and quiet satisfaction. Warm golden light pours through large arched windows. The space is airy, not cluttered — lots of breathing room. Warm palette of terracotta, sage green, golden sand, parchment cream, deep umber. No teal, no mint, no mauve. 16:9.
```

---

## Placement & Story Arc

| # | Section | Beat | Robot's arc |
|---|---------|------|-------------|
| 1 | Hero / Title | Lost in the framework factory | Confused — lens dim, antenna drooping |
| 2 | The Moment It Clicked | You write down your process | Curious — lens brightening, antenna perked |
| 3 | What Actually Worked | You hand it the manual | Understanding — lens bright, antenna straight |
| 4 | Real Results / Broader Pattern | It replicates your process at scale | Mastery — all lenses glowing, working independently |

## Model Settings

- **Aspect ratio:** Always 16:9 (`1792x1024` on DALL-E, `--ar 16:9` on Midjourney)
- **Midjourney:** `--ar 16:9 --style raw --v 7 --no teal, mint, mauve, purple, photorealistic, R2D2, Star Wars`
- **Character consistency:** Generate image 1 first. If you like the robot design, use character reference / image-to-image to keep it consistent across 2-4.
- **If text artifacts appear:** Add "no text, no labels, no watermarks" to the prompt.
