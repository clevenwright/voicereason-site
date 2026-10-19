# voicereason-site

Public marketing site for VoiceReason.AI (https://www.voicereason.ai): AI phone practice for sales teams. A team member dials a number, practices a real conversation with an AI buyer, gets a written report, and on Practice + Coach a live AI coach comes on the same call.

Static site on Vercel: index.html, how-it-works.html, onboarding.html, recording.html, assets/. Made by Pyrigen Incorporated, Texas.

## Prices live in two places

The plan cards in index.html (#plans) and the SoftwareApplication offers in the JSON-LD. Change both in the same commit. scripts/check_schema_prices.py compares them, and the schema-price-guard workflow fails when they differ.
