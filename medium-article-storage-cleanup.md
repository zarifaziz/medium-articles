# Your Mac Will Fill Up. It Always Does. This Time I Let AI Deal With It.

You know how it goes. You buy a new MacBook. You tell yourself "256GB will be fine." Or you splurge on 512GB thinking "I'll never fill this."

Six months later: *"Your disk is almost full."*

It doesn't matter how much storage you start with. Macs fill up. And every few months you face the dreaded spring cleaning — clicking through folders, guessing what's safe to delete, never making real progress.

This time I tried something different. I asked an AI agent to investigate.

It found 128GB of hidden junk in about 20 minutes.

---

## The macOS Storage Problem

If you've ever opened **System Settings → Storage**, you know the frustration.

![Before cleanup](/Users/zariftutero/Pictures/Cleanshot/CleanShot 2026-01-23 at 00.00.03@2x.png)

"Documents" taking 91GB? My actual Documents folder was 129MB. Where was the other 90GB?

Apple's storage categories are misleading. "Documents" includes app caches buried in `~/Library` and basically anything macOS can't categorize elsewhere. The UI wants you to click "Store in iCloud" — which conveniently requires paying for more storage.

---

## Asking the AI

I opened Cursor (which runs Claude as a coding assistant) and typed:

> "I feel like my Docker has a secret cache somewhere. Can you verify?"

I didn't ask it to clean my whole Mac. I just had a hunch about Docker.

But the AI went further. It checked Library caches, npm, yarn, Docker, Chrome, Slack and about a dozen other locations. All in parallel. Within seconds I had a complete breakdown.

The 17GB Cursor auto-updater cache was a surprise. The 9.7GB npm cache less so. The 5GB Notion was hoarding for "offline access"? News to me.

---

## A Note on Safety

Letting an AI run shell commands is risky. But a few things made this safe:

**It asked permission before every action.** I had to approve each batch of deletions.

**Everything was cache files.** Stuff that rebuilds automatically — npm cache, Chrome Service Workers, Go build cache.

**I verified before running.** I could see exactly what folder it was targeting and why.

The model's intelligence matters. A less capable model might not distinguish between cache and actual files. Opus was cautious throughout.

---

## What It Found

The big offenders:
- Cursor auto-updater — 17GB
- npm cache — 9.7GB
- Chrome/Slack/Notion caches — 12GB combined
- Docker images — 5.6GB
- Python/Go/Yarn caches — 13GB combined
- Old `node_modules` folders — 4GB

That 91GB "Documents"? Actually `~/Library` (78GB of caches) plus my code projects. Real Documents folder: 129MB.

---

## The Result

The AI cleaned in batches:

**Round 1:** 480GB → 419GB  
**Round 2:** 419GB → 394GB  
**Round 3:** 394GB → 352GB

![After cleanup](/Users/zariftutero/Pictures/Cleanshot/CleanShot 2026-01-23 at 09.33.55@2x.png)

**128GB freed.** My Mac can breathe again.

---

## Takeaways

**Developer tools hoard storage.** npm, yarn, pip, go, Docker — they all cache forever and never self-clean.

**macOS lies about "Documents."** It's actually `~/Library/Caches` and `~/Library/Application Support`.

**AI agents are good at boring tasks.** It checked places I wouldn't have thought of and explained everything before acting.
