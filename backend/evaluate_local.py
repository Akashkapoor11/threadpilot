import json
from pathlib import Path
from app.engine import local_extract

cases=json.loads((Path(__file__).resolve().parents[1]/"data/evaluation_cases.json").read_text())
tp=fp=fn=0
for c in cases:
    expected=set(c["expected"]); predicted={x["type"] for x in local_extract(c["text"])["signals"]}
    tp+=len(expected&predicted); fp+=len(predicted-expected); fn+=len(expected-predicted)
precision=tp/(tp+fp) if tp+fp else 0
recall=tp/(tp+fn) if tp+fn else 0
f1=2*precision*recall/(precision+recall) if precision+recall else 0
print(f"Precision={precision:.3f} Recall={recall:.3f} F1={f1:.3f}")
