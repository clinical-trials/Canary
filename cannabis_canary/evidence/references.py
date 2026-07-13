"""Curated dosing / route-of-ingestion references for clinician review.

Real human- and rodent-pharmacokinetics literature only — no fabricated
citations. Sourced from the reviews the project selected (Godbole et al.,
Med Cannabis Cannabinoids 2026; and the Permanente Journal PK review) plus
the foundational human-PK papers they cite. Links use a DOI when it is known
for certain, otherwise a PubMed search for the citation.
"""
from __future__ import annotations

import urllib.parse


def _pubmed(term: str) -> str:
    return "https://pubmed.ncbi.nlm.nih.gov/?term=" + urllib.parse.quote(term)


DOSING_REFERENCES: tuple[dict, ...] = (
    {
        "citation": "Godbole SS, Raup-Konsavage WM, Vrana KE. Pharmacokinetics of "
                    "Cannabinoids Delivered by Diverse Routes in Rodents. Med "
                    "Cannabis Cannabinoids. 2026;9(1):150–162.",
        "url": "https://doi.org/10.1159/000551979",
    },
    {
        "citation": "Mechanisms of Action and Pharmacokinetics of Cannabis. "
                    "The Permanente Journal (TPP/19.200).",
        "url": "https://doi.org/10.7812/TPP/19.200",
    },
    {
        "citation": "Huestis MA. Human cannabinoid pharmacokinetics. Chem "
                    "Biodivers. 2007;4(8):1770–1804.",
        "url": _pubmed("Huestis human cannabinoid pharmacokinetics Chem Biodivers 2007"),
    },
    {
        "citation": "Lucas CJ, Galettis P, Schneider J. The pharmacokinetics and "
                    "pharmacodynamics of cannabinoids. Br J Clin Pharmacol. "
                    "2018;84(11):2477–2482.",
        "url": _pubmed("Lucas pharmacokinetics pharmacodynamics cannabinoids Br J Clin Pharmacol 2018"),
    },
    {
        "citation": "Grotenhermen F. Pharmacokinetics and pharmacodynamics of "
                    "cannabinoids. Clin Pharmacokinet. 2003;42(4):327–360.",
        "url": _pubmed("Grotenhermen pharmacokinetics pharmacodynamics cannabinoids Clin Pharmacokinet 2003"),
    },
    {
        "citation": "Stella B, et al. Cannabinoid formulations and delivery "
                    "systems: current and future options to treat pain. Drugs. "
                    "2021;81(13):1513–1557.",
        "url": _pubmed("Stella cannabinoid formulations delivery systems Drugs 2021"),
    },
    {
        "citation": "Lodzki M, et al. Cannabidiol—transdermal delivery and "
                    "anti-inflammatory effect in a murine model. J Control "
                    "Release. 2003;93(3):377–387.",
        "url": _pubmed("Lodzki cannabidiol transdermal delivery murine J Control Release 2003"),
    },
    {
        "citation": "Bansal S, et al. Predicting the potential for cannabinoids "
                    "to precipitate pharmacokinetic drug interactions via "
                    "inhibition/inactivation of major cytochromes P450. Drug "
                    "Metab Dispos. 2020;48(10):1008–1017.",
        "url": _pubmed("Bansal cannabinoids pharmacokinetic drug interactions cytochrome P450 Drug Metab Dispos 2020"),
    },
)
