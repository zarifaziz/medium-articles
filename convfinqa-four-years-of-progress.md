# Four Years of Progress: Revisiting a 2022 Financial QA Benchmark with a 2026 Frontier Model

Read an AI paper from 2022 and you'll spot the pattern instantly. Real problem. Clever solution. Then the architecture: retrieval pipeline, custom encoder, domain-specific language, careful fine-tuning — and you find yourself wondering: *what happens if you just don't do any of that?*

That's more or less what this project was. I took the ConvFinQA benchmark, stripped out the 2022 architecture, and asked a frontier model to do the same job with a prompt and a typed tool.

The result: 83.5% per-turn accuracy — 14.6 points better than the 2022 best, with no retriever, no DSL, and no fine-tuning. And a finding that's more interesting than the headline number.

---

## The Problem

ConvFinQA is a dataset of multi-turn conversational questions over SEC financial filings. A typical conversation goes like this: *"What was revenue in 2018?"*, then *"And in 2017?"*, then *"So what was the growth rate?"* Each answer builds on the last. The document — a table plus surrounding narrative — stays fixed; the conversation accumulates.

What makes it hard is the combination: you need to find the right cell in a financial table, apply arithmetic, and do it consistently across a conversation where earlier errors cascade forward. The 2022 ConvFinQA paper attacked this with a retriever-then-generator pipeline. The retriever pulled relevant facts from the document; the generator produced a domain-specific program — something like `subtract(206588, 181001)` — that an executor then evaluated. The best model, FinQANet, hit 68.9% execution accuracy on the dev split.

---

## The 2026 Approach

The 2022 pipeline was exactly right for 2022. Long context wasn't reliable. Structured outputs required custom DSLs. Fine-tuning was the main lever.

None of those constraints apply anymore.

The median document in ConvFinQA is around 675 tokens. It fits cleanly in a system prompt. The conversation history — prior questions and the model's own previous answers — replays as a message list. No retrieval needed. For structure, I used a Pydantic model with forced `tool_choice` instead of a DSL:

```python
class SubmitAnswer(BaseModel):
    reasoning: str = Field(description="Step-by-step reasoning for the answer.")
    calculation: str = Field(
        description="Arithmetic expression that produced the answer, e.g. '206588 - 181001'."
    )
    sign_convention: Literal["magnitude", "signed", "n/a"] = Field(
        description=(
            "Does the question want a signed value (direction matters) or a magnitude (size only)? "
            "'signed' for arithmetic results — change, difference, X minus Y, net values. "
            "'magnitude' when the question names an inherently non-negative quantity (rate, yield, "
            "loss, charge) and the table's negative sign is a display convention. "
            "'n/a' only for yes/no questions."
        )
    )
    answer: str = Field(
        description=(
            "Final answer as a string. Numbers as plain digits "
            "(e.g. '25587', '0.141', '14.1'); booleans as 'yes' or 'no'."
        )
    )
    unit: Literal["raw", "percent", "ratio", "none"] = Field(
        description=(
            "Unit hint for the answer. 'raw' for absolute numbers, "
            "'percent' for percentages (e.g. '14.1' meaning 14.1%), "
            "'ratio' for unitless fractions, 'none' if not applicable."
        )
    )
```

Forced `tool_choice` reduces output parsing to schema validation: either the response parses or it fails loudly. No regex. No DSL executor. No custom tokenizer. The `sign_convention` field exists because financial tables use parentheses as a display convention (a loss shown as `(433)` rather than `-433`), and without an explicit decision point the model would flip between conventions inconsistently — an easy fix once you name the problem.

---

## What Changed

| Paper (2022) | This approach (2026) |
|---|---|
| DSL program is the generation target | DSL is eval metadata; tool-use emits typed `SubmitAnswer` |
| Retriever-then-generator pipeline | No retriever — doc fits in the system prompt |
| Execution accuracy only | Per-turn + per-conversation + conditional accuracy |
| Custom encoder for table and text | Markdown rendering, verbatim cells |
| FinQANet **68.9%** dev (with retrieval) | **83.5%** per-turn (no retrieval, no fine-tuning) |

The 2022 DSL approach wasn't wrong — it was the right engineering call for the tools available then. By 2026, the model can do the arithmetic itself and express its output in a typed schema. The DSL became a translation layer solving a problem that no longer exists.

---

## Finding 1: 83.5% With No Domain Stack

On the full 421-record dev split (1,490 turns), `claude-sonnet-4-6` with the above setup hit **83.5% per-turn accuracy** and **73.6% per-conversation accuracy** (every turn correct). Total cost: $19.04. Wall time: 72 minutes. Human experts on the same benchmark score **89.4%**. This sits 5.9 points below that ceiling — and 14.6 points above the 2022 best, without touching the model weights.

That gap says something about where the headroom actually was. It wasn't in the architecture. It was in the model.

---

## Finding 2: The Late-Turn Degradation Claim Doesn't Reproduce

The 2022 paper reported that "later turns in the conversations tend to be harder to answer due to longer reasoning dependencies," and that "if the prediction for any turn is wrong, then there is a very minor chance that the subsequent turns are correct." That was a real finding in 2022. It shaped the paper's architecture and would shape any serious follow-up work. It doesn't hold anymore.

To test it properly, I tracked two curves: **marginal accuracy** (raw accuracy at turn position t1, t2, t3…) and **conditional accuracy** — the probability that turn *i* is correct given that turn *i–1* was also correct. These two measures come apart in a useful way. If marginal accuracy falls with turn index, that could mean either the model degrades on longer context, or it's just compounding earlier errors. Conditional accuracy separates the two: if conditional accuracy stays flat while marginal drops, the model isn't degrading — it's cascading.

Both curves are essentially flat. Conditional accuracy sits at 92–94% from t1 through t5. Marginal accuracy sits at 83–85%. The drop in per-conversation accuracy is exactly what you'd expect from an 84% independent error rate compounding over ~3.5 turns. The model-degradation effect the 2022 paper observed has effectively been engineered out of frontier models by long-context training.

That has direct implications for where to spend effort. Context summarisation, sliding windows, attention management — none of it addresses the actual failure mode. The failure mode is upstream: a bad cell selection in turn 1 propagates through turns 2, 3, and 4 because the model's own prior answers replay as history. Fix the cell-selection error and you fix the cascade. The long-context problem is already solved.

---

## What This Tells Us

The ConvFinQA dataset is a genuinely well-designed benchmark and the paper's analysis is sharp. What this experiment shows is how fast the ground shifts.

In four years, a capability that required a retriever, a fine-tuned encoder, a DSL, and an executor can be matched — and beaten — with a prompted API call and a typed Pydantic schema. The 2022 team's architecture was careful, justified engineering. From 2026, it reads as scaffolding built around constraints that no longer exist.

The residual failures are real and interesting: a few hundred turned on financial sign conventions, duplicate column disambiguation, and data alignment issues in the cleaned dataset. But those are not 2022-era problems. They're edge cases in a tool that largely works.

The code for this is at [REPO LINK].

---

*Zarif Aziz is CTO & Co-Founder at [Auralis](https://www.auralis.solutions/), building AI-powered solutions for enterprise clients. Connect on [LinkedIn](https://www.linkedin.com/in/zarifaziz/) or [GitHub](https://github.com/zarifaziz).*
