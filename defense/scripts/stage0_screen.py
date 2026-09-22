import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

D2P2_MENTION = re.compile(r"DIRECT[- ]TO[- ]PHASE[- ](?:II|2)|\(D2P2\)|\(DP2\)|\(DPII\)")
# phrasing that means Phase I proposals are NOT accepted (D2P2-only topic)
D2P2_ONLY = re.compile(
    r"(?:DIRECT[- ]TO[- ]PHASE[- ](?:II|2)|D2P2|DP2|DPII)[^.]{0,60}\bONLY\b"
    r"|PHASE I (?:PROPOSALS|AWARDS) WILL (?:BE REJECTED|NOT BE (?:MADE|EVALUATED|ISSUED|ACCEPTED))"
    r"|NO PHASE I AWARDS? (?:ARE|IS|WILL BE) (?:ANTICIPATED|MADE)"
    r"|(?:A )?FORMAL PHASE I AWARD WILL NOT BE ISSUED"
    r"|INTENDED FOR TECHNOLOGY PROVEN READY TO MOVE DIRECTLY INTO PHASE II"
    r"|THIS IS A DIRECT[- ]TO[- ]PHASE[- ](?:II|2)(?: \(D2P2\))? TOPIC"
    r"|AS A REQUIREMENT OF THIS DIRECT TO PHASE II"
    r"|(?:SOLICITATION|TOPIC) IS FOR A DIRECT[- ]TO[- ]PHASE[- ](?:II|2)"
    r"|THIS DIRECT[- ]TO[- ]PHASE[- ](?:II|2)(?: \((?:D2P2|DP2)\))? (?:SBIR|STTR|TOPIC|EFFORT)"
    r"|PHASE I WORK IS EXPECTED TO HAVE BEEN COMPLETED"
)


def d2p2_status(title, desc):
    if "DIRECT TO PHASE II" in title:
        return "only"
    if D2P2_ONLY.search(desc):
        return "only"
    if D2P2_MENTION.search(desc):
        return "optional"
    return "none"


def run_stage_0(csv_path=RAW / "topics_search_1789872938.csv",
                output_path=PROCESSED / "stage0_survivors.csv"):
    df = pd.read_csv(csv_path)
    df['Topic Description'] = df['Topic Description'].fillna("")

    survivors = []
    for _, row in df.iterrows():
        title = str(row.get('Topic Title', '')).upper()
        desc = str(row.get('Topic Description', '')).upper()
        topic_num = str(row.get('Topic Number', ''))

        # T0.1 D2P2 -> STOP only when Phase I proposals are not accepted
        d2p2 = d2p2_status(title, desc)
        if d2p2 == "only":
            continue

        # Empty description -> STOP (cannot triage without text)
        if not desc.strip():
            continue

        flags = []
        if d2p2 == "optional":
            flags.append("T0.1 D2P2 also accepted (Phase I still open)")
        # T0.2 STTR Check
        if (len(topic_num) > 5 and topic_num[5] == 'T') or str(row.get('Program')).upper() == 'STTR':
            flags.append("STTR: Requires RI partner")

        # T0.3 Clearances Check
        classified_terms = ['CLASSIFIED', 'NO FOREIGN INFLUENCE', 'FACILITY CLEARANCE', 'ITAR', '32 U.S.C. § 2004.20']
        for term in classified_terms:
            if term in desc or term in title:
                flags.append(f"T0.3 {term}")

        # T0.4 Registration
        flags.append("T0.4 Registration check")

        survivors.append({
            'Topic Number': topic_num,
            'Topic Title': row.get('Topic Title', ''),
            'Branch': row.get('Branch', ''),
            'Program': row.get('Program', ''),
            'Close Date': row.get('Close Date', ''),
            'Description': row.get('Topic Description', ''),
            'Flags': " | ".join(flags)
        })

    pd.DataFrame(survivors).to_csv(output_path, index=False)
    print(f"Stage 0 complete. {len(survivors)} topics advanced to {output_path}.")

if __name__ == "__main__":
    run_stage_0()
