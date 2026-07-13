"""Curated dosing / route-of-ingestion references for clinician review.

Real human- and rodent-pharmacokinetics literature only — no fabricated
citations, DOIs, or IDs. Each entry carries whatever identifiers are VERIFIED
(doi / pmid / pmcid); entries lacking a verified id fall back to a precise
PubMed search term. The template turns these into DOI, PubMed, PMC-PDF, and
"look up" links.
"""
from __future__ import annotations

DOSING_REFERENCES: tuple[dict, ...] = (
    {
        "citation": "Godbole SS, Raup-Konsavage WM, Vrana KE. Pharmacokinetics of "
                    "Cannabinoids Delivered by Diverse Routes in Rodents. Med "
                    "Cannabis Cannabinoids. 2026;9(1):150–162.",
        "doi": "10.1159/000551979",
        "pmid": "42367575",
        "pmcid": "PMC13299164",
    },
    {
        "citation": "Upadhyay G, Fihurka O, Habecker C, Patel P, Sanchez-Ramos J. "
                    "Measurement of Δ9-THC and metabolites in the brain and "
                    "peripheral tissues after intranasal instillation of a "
                    "nanoformulation. J Cannabis Res. 2023;5:3.",
        "doi": "10.1186/s42238-022-00171-8",
        "pmid": "36750917",
        "pmcid": "PMC9903512",
    },
    {
        "citation": "Mechanisms of Action and Pharmacokinetics of Cannabis. "
                    "The Permanente Journal (TPP/19.200).",
        "doi": "10.7812/TPP/19.200",
        "search": "Mechanisms of Action and Pharmacokinetics of Cannabis Permanente Journal",
    },
    {
        "citation": "Huestis MA. Human cannabinoid pharmacokinetics. Chem "
                    "Biodivers. 2007;4(8):1770–1804.",
        "search": "Huestis human cannabinoid pharmacokinetics Chem Biodivers 2007",
    },
    {
        "citation": "Lucas CJ, Galettis P, Schneider J. The pharmacokinetics and "
                    "pharmacodynamics of cannabinoids. Br J Clin Pharmacol. "
                    "2018;84(11):2477–2482.",
        "search": "Lucas Galettis pharmacokinetics pharmacodynamics cannabinoids Br J Clin Pharmacol 2018",
    },
    {
        "citation": "Grotenhermen F. Pharmacokinetics and pharmacodynamics of "
                    "cannabinoids. Clin Pharmacokinet. 2003;42(4):327–360.",
        "search": "Grotenhermen pharmacokinetics pharmacodynamics cannabinoids Clin Pharmacokinet 2003",
    },
    {
        "citation": "Stella B, et al. Cannabinoid formulations and delivery "
                    "systems: current and future options to treat pain. Drugs. "
                    "2021;81(13):1513–1557.",
        "search": "Stella cannabinoid formulations delivery systems Drugs 2021",
    },
    {
        "citation": "Lodzki M, et al. Cannabidiol—transdermal delivery and "
                    "anti-inflammatory effect in a murine model. J Control "
                    "Release. 2003;93(3):377–387.",
        "search": "Lodzki cannabidiol transdermal delivery murine J Control Release 2003",
    },
    {
        "citation": "Bansal S, et al. Predicting the potential for cannabinoids "
                    "to precipitate pharmacokinetic drug interactions via "
                    "inhibition/inactivation of major cytochromes P450. Drug "
                    "Metab Dispos. 2020;48(10):1008–1017.",
        "search": "Bansal cannabinoids pharmacokinetic drug interactions cytochrome P450 Drug Metab Dispos 2020",
    },
)
