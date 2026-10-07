"""Fail when the published plan-card prices and the JSON-LD offer prices differ.

The plan cards in index.html (#plans) are the source of truth a person reads.
The SoftwareApplication offers in the JSON-LD are what search engines quote.
A stale schema price is a published price we are not honouring, so this check
fails loudly on any difference. Standard library only.
"""
import json
import re
import sys
from pathlib import Path

html = Path(__file__).resolve().parent.parent.joinpath("index.html").read_text(encoding="utf-8")


def card_prices():
    sec = re.search(r'<section id="plans">(.*?)</section>', html, re.S)
    if not sec:
        sys.exit("FAIL: #plans section not found")
    found = set()
    for block in re.findall(r'<p class="eyebrow">([^<]+)</p>\s*<div class="price-fig">(.*?)</div>', sec.group(1), re.S):
        plan, fig = block[0].strip(), re.sub(r"<[^>]+>", " ", block[1])
        for amount, period in re.findall(r"\$([\d,]+)\D*?per seat, per (month|year)", fig):
            found.add((plan, amount.replace(",", ""), period))
    return found


def schema_prices():
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if not m:
        sys.exit("FAIL: JSON-LD block not found")
    graph = json.loads(m.group(1)).get("@graph", [])
    apps = [n for n in graph if n.get("@type") == "SoftwareApplication"]
    if len(apps) != 1:
        sys.exit("FAIL: expected exactly one SoftwareApplication, found %d" % len(apps))
    found = set()
    for offer in apps[0].get("offers", []):
        plan = offer["name"].split(",")[0].strip()
        unit = offer.get("priceSpecification", {}).get("unitText", "")
        period = "year" if unit.endswith("per year") else "month" if unit.endswith("per month") else "?"
        if offer.get("priceCurrency") != "USD":
            sys.exit("FAIL: offer %s is not USD" % offer["name"])
        if str(offer.get("price")) != str(offer.get("priceSpecification", {}).get("price")):
            sys.exit("FAIL: offer %s price and priceSpecification differ" % offer["name"])
        found.add((plan, str(offer["price"]), period))
    for banned in ("Review", "AggregateRating"):
        if '"@type":"%s"' % banned in m.group(1).replace(" ", ""):
            sys.exit("FAIL: %s found in JSON-LD; we have no customer reviews" % banned)
    return found


cards, schema = card_prices(), schema_prices()
if not cards:
    sys.exit("FAIL: no prices parsed from the plan cards")
if cards != schema:
    print("FAIL: plan cards and schema prices differ")
    print("  only on cards :", sorted(cards - schema))
    print("  only in schema:", sorted(schema - cards))
    sys.exit(1)
print("OK: %d prices match: %s" % (len(cards), sorted(cards)))
