# I Tried Every Prompt Optimization Framework. Here's What Actually Worked.

If you're building LLM systems in production, you've probably looked at prompt optimization frameworks — DSPy, GEPA, MIPRO. The pitch is compelling: define your pipeline, pick an optimizer, and let it search for better prompts automatically.

I spent weeks going all in on this. Full optimization pipelines, hundreds of iterations, Weights & Biases tracking, anti-memorization safeguards, stratified train/test splits. The works.

The result? Marginal gains I couldn't replicate in production. Scores that fluctuated wildly between runs. An optimized judge that was simultaneously harsher *and* dumber. A "73% pass rate" inside the framework that dropped to 64% when I ran the same prompt through our actual eval pipeline.

Then I tried something embarrassingly simple: I gave an AI agent a markdown file describing *how I optimize prompts*, pointed it at the codebase, and let it run experiments. It outperformed every framework I'd tried — and the improvements actually stuck in production.

This article is about why prompt optimization frameworks break down at complexity, and what works instead.

---

## Some Context

I'm Zarif, Lead AI Engineer at [Tutero](https://www.tutero.com), an ed-tech company building AI-powered tutoring for thousands of students across Australia. A core part of what we do is generate educational content at scale — 7+ different content types, each with its own generation pipeline.

Each content type runs through the same pattern: a generation step that produces multiple candidates, a selection step that picks and refines the best one, and an LLM judge that scores the final output against our quality rubric.

[IMAGE: Pipeline diagram — Generation (N calls) → Selection & Refine → Judge (PASS/FAIL + critique)]

When you have this many content types, each with their own generation and scoring prompts, prompt engineering becomes a full-time job. So naturally, I went looking for ways to automate it.

---

## The DSPy Experiment

[DSPy](https://dspy.ai/) is a prompt optimization framework out of Stanford. Instead of manually tweaking prompts, you define your pipeline programmatically and let an optimizer search for better instructions, few-shot examples, or both.

I used GEPA (Genetic Pareto Optimization) specifically — a self-reflection algorithm where a teacher LLM reviews failures from the current prompt, proposes improvements, and iterates. It consistently outperforms MIPRO and other alternatives in DSPy.

[IMAGE: GEPA optimization loop — Current Prompt → Run on Training Batch → Judge Evaluates → Teacher LLM Reflects on Failures → Propose Improved Instruction → Compare to Best → Loop]

### The setup

We built a proper pipeline around it:

```python
config = DSPyOptimizerConfig(
    node_type="ContentTypeA",

    # Training data (200 synthetic examples)
    generation_dataset_path="fixtures/generation_optimization/content_a_200samples.csv",

    # Holdout test set (100 examples, never seen during optimization)
    holdout_dataset_path="fixtures/api_evaluation_datasets/content_a_100samples.csv",

    # Train/val split — GEPA needs largest trainset, smallest val
    train_ratio=0.7,
    val_ratio=0.3,

    # Models
    student_model="cerebras/gpt-oss-120b",   # Fast inference (~3500 TPS)
    teacher_model="openai/gpt-5.2",           # Reflects on failures

    # GEPA budget
    max_optimization_evals=50,
    reflection_minibatch_size=20,

    # Anti-memorization safeguards
    use_anti_memorization_system_prompt=True,

    # W&B tracking
    wandb_project="content-a-generator-optimization",
)

optimized_prompt, output_path = optimize_generation_workflow(config)
```

Two-step pipeline: first optimize the judge (up to 300 GEPA iterations to align with human labels), then optimize the generator (up to 50 iterations using the calibrated judge as feedback). Anti-memorization safeguards, W&B tracking, stratified splits — the whole nine yards.

### What actually happened

It did *something*. Our pass rate on one content type went from 43% to 53%. But when I read the outputs, the judge had become miscalibrated — too harsh, failing things for trivial misunderstandings, not applying common sense. The score "improved" partly because DSPy created a stricter judge that happened to agree with itself more.

The real kicker: **when I extracted the optimized prompt and ran it through our normal eval pipeline, the score dropped from the 73% DSPy was reporting to 64%.** Same prompt, same data — different scaffolding. The improvement was partially an artifact of DSPy's own evaluation setup.

Scores were also inconsistent across runs with the same config: 45%, then 63%, then 60%, then 55%. I spent days trying to figure out what was real.

---

## Why Frameworks Hit a Ceiling

The fundamental issue isn't that DSPy is bad software — it's well-built and the GEPA algorithm is genuinely clever. The problem is structural.

### They can only see the prompt string

This is the fatal flaw.

[IMAGE: Side-by-side comparison — "What DSPy Can See" (just the prompt instruction string) vs "What a Prompt Engineer Can See" (generator prompt, selector prompt, judge prompt, response models, task functions, trace logs, git history, downstream parsers, pipeline code, common fragments, template engine, eval tooling)]

DSPy optimizes the *instruction text*. That's it. It can swap out few-shot examples, reword the system prompt, add constraints — all within the boundary of a single string.

But when I sit down to improve a prompt, I'm not just editing text. I'm reading the scorer to understand *why* things fail. I'm inspecting traces to see if candidates are bad or if selection is bad. I'm checking if the response model constrains output in unexpected ways. I'm looking at the downstream service that parses the structured output. I'm considering whether the whole architecture should change.

A framework has no visibility into any of this. It's optimizing one knob in a system with dozens.

### They can't make architectural changes

Some of our biggest improvements had nothing to do with prompt wording. For example, we discovered that generating 3 candidates in a single LLM call caused them to be "entangled" — each candidate conditioned on the previous ones, leading to shared systematic flaws.

The fix was architectural: split into 3 parallel independent calls, each generating 1 candidate.

[IMAGE: Before/After diagram — BEFORE: Single LLM Call with Candidate 1 → 2 → 3 (entangled, shared flaws propagate) vs AFTER: Three parallel independent calls, each producing one fresh candidate → Select Best]

That single change — not a prompt edit — took our holdout pass rate from 70% to 79%. No prompt optimization framework would ever discover this. It requires understanding the code, the execution model, and the *reasons* behind failure patterns.

### Optimized prompts don't transfer cleanly

Even when DSPy found a better prompt, integrating it was painful. The optimized prompt existed inside DSPy's module system with its own serialization format and runtime assumptions. Extracting it into our production template system required manual surgery every time.

And often, the "optimized" prompt encoded specific training examples into the instructions (despite anti-memorization safeguards), or added constraints that made sense for 200 training samples but broke edge cases in production.

---

## The Moment It Clicked

While I was wrestling with DSPy configs, I'd already been using an agentic coding tool for day-to-day development. One afternoon, frustrated after yet another DSPy run that produced a "better" prompt I couldn't use, I just asked the agent to look at some failing evaluations and tell me what was going wrong.

It read the scorer prompt. It read the generation prompt. It pulled up trace logs. It spotted that the scorer was penalizing a certain answer format but the generation prompt had no rule against it. It edited the prompt, re-ran the eval, and the pass rate jumped 10 points.

That entire loop — the exact same loop I'd been trying to automate with hundreds of lines of optimization pipeline code — happened in about 3 minutes. No optimizer. No GEPA iterations. Just an AI reading code, forming a hypothesis, and testing it.

That was when I realized: I don't need an optimization algorithm. I need to encode my process into something an agent can follow, give it the same tools I use, and get out of its way.

---

## What Actually Worked: Agent Skills

I formalized the approach into **skills** — structured markdown files that describe a workflow, reference key files, and give the agent the context it needs to work autonomously.

A skill doesn't optimize a prompt string. It gives the agent the same workflow and tools that *I* use as a prompt engineer, and lets it operate.

### What a skill looks like

Here's the core of our **generator optimization skill** — the actual markdown file the agent reads before starting:

```markdown
# Generator Prompt Optimization

## Goal
Maximize the judge pass rate for a given content type's generator prompt
through iterative experimentation.

## Core Philosophy
You are an expert prompt engineer. Think architecturally about the
problem - consider both low-level prompt edits AND high-level structural
changes. Form hypotheses, run experiments, analyze results, iterate.

**Trust but verify the judge.** If the judge fails an output, there's
likely a real issue — but judges can be miscalibrated. Your first job is
to validate that failures are legitimate before fixing the generator.
```

### The triage process

Then comes the part I think matters most — the triage process. This is where expert heuristics live, and it's the thing no framework can replicate:

```markdown
## Triage Before Analysis

Before running clustering or batch analysis, manually inspect 3-5
FAIL cases:

1. **Read the critique reasoning**, not just the verdict
2. **Ask: Is this critique correct?**
   - If clearly wrong → Stop. Flag to human. Exit optimization.
   - If correct but trivial → Note it, check for pattern
   - If correct and substantive → This is your optimization target

**Early exit rule**: If you find an obviously wrong critique in your
first 5 cases, exit and ask your superior to fix the judge.
Don't analyze 50 failures with a broken judge.

**Greedy fixing**: If you find an obvious, high-impact fix in your
first few cases, make it immediately and re-run.
```

### Thinking beyond prompt text

And the scope — this is key. The skill explicitly tells the agent to think beyond prompt text:

```markdown
## Experimentation Mindset

Consider beyond prompt edits:
- **Ensemble pattern** for content types with low pass rates
- **Scaling inference time compute** to let the LLM think longer
- **Chain-of-thought fields** to help models reason before output
- **Prompt chains** — multiple focused calls vs one overloaded call
- **Complexity rebalancing** between generation and selection
```

We have similar skills for judge optimization (with decision trees for diagnosing model-vs-human disagreements) and for running prompt experiments in isolated git worktrees. They all follow the same principle: encode your expertise, provide the tools, let the agent operate.

### What the agent actually does

Here's what an actual optimization session looks like:

```bash
# Agent reads the relevant files first
> Read src/prompting/tasks/content_type_a.py
> Read src/prompting/scorers/content_type_a.py
> Read src/prompting/tasks/common.py

# Runs a baseline evaluation
> uv run python -m prompting.commands.evaluate \
    --source synthetic --node-type ContentTypeA --quantity 50
# → Pass rate: 24% (12/50)

# Inspects failures — reads the judge's critique, not just the verdict
> uv run python -m prompting.commands.analyze \
    data/eval_results/content_a_eval.csv \
    --disagreements-only

# Spots a pattern: "Answers are using yes/no format"
# Forms hypothesis: ban binary answer formats in generation prompt

# Edits the prompt template directly in the codebase
> Edit src/prompting/tasks/content_type_a.py
  + "NEVER use yes/no questions or binary answer formats"

# Re-runs evaluation
> uv run python -m prompting.commands.evaluate \
    --source synthetic --node-type ContentTypeA --quantity 50
# → Pass rate: 34% (17/50) — +10pp improvement

# Commits, then continues with next hypothesis...
> git commit -m "content_type_a: ban binary answer formats"
```

This is exactly what I do. Except it does it faster, doesn't get tired, and can run experiments back-to-back while I'm in meetings.

### No extraction step

The crucial thing: because the agent operates in the actual codebase, every improvement is *immediately* integrated. There's no extraction step, no manual surgery, no replication gap. It edits the real files, runs the real eval pipeline, and commits the real changes.

---

## Real Results

Here are actual numbers from our agent-driven optimization.

### Content Type A (Complex with Context Dependencies)

| Metric | Baseline | After Agent | Improvement |
|--------|----------|-------------|-------------|
| Training (50 samples) | 24% | 44-56% | +20-32pp |
| Holdout (100 samples) | 40% | 60% | **+20pp** |

The agent made 7 distinct changes including structural fixes, selection improvements, and generation tweaks. It also identified that ~3% of remaining failures were judge miscalibration — not something it could fix from the generator side.

### Content Type B (Ensemble Experiment)

| Run | n | Pass Rate | Type |
|-----|---|-----------|------|
| Baseline (pre-optimization) | 100 | 62% | Pre-commit |
| Baseline (committed) | 100 | 70% | Committed |
| Independent gen (parallel) | 50 | 80% | Training |
| **Holdout (unseen data)** | **100** | **79%** | **Holdout** |

The key change was architectural: switching from sequential to parallel independent generation. The agent also documented what *didn't* work — 5 candidates in 1 call (56%), end-of-prompt reminders (regression) — which is exactly the kind of negative result logging that frameworks never give you.

### What didn't work matters too

That negative result logging deserves emphasis. When DSPy runs 50 iterations, the failed attempts just vanish into W&B noise. But when an agent tries something, sees it regress, and documents *why* it didn't work, that knowledge compounds. Future optimization sessions can skip dead ends.

### Across All Content Types

Once we let the agent drive optimization across all 7+ content types, we saw pass rate improvements ranging from **+7pp to +55pp** depending on the content type. Every single one improved.

[IMAGE: Results table showing before/after pass rates across content types with improvement column]

---

## The Broader Pattern: Get Out of the Way

This isn't just a prompt engineering insight. There's a growing recognition across AI tooling that the best way to get results from LLMs is to *stop constraining them*.

The Amp team wrote about [building a coding agent](https://ampcode.com/notes/how-to-build-an-agent) in under 400 lines of code. Their thesis: an agent is just an LLM, a loop, and enough tokens. The magic isn't in the framework — it's in getting out of the model's way.

Mario Zechner built [pi](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/), a minimal coding agent with four tools, a system prompt under 1,000 tokens, and no artificial constraints. It competed with agents 10x its complexity.

[Hamel Husain](https://x.com/HamelHusain) — who's worked with 50+ companies on LLM evals — recently released [evals-skills](https://github.com/hamelsmu/evals-skills), an open-source set of skills that teach AI agents how to build evaluations, audit pipelines, analyze errors, and write judge prompts. Same pattern: encode expert knowledge into skill files, give the agent tools, let it work. The fact that someone with that breadth of experience arrived at the same approach independently is telling.

The pattern keeps showing up: **the less you constrain the model, the better it performs.** Frameworks constrain. Rigid optimization algorithms constrain. A skill file that says "here's the goal, here are the tools, here's how I think about the problem — now go" gives the model room to actually *think*.

### Side-by-side comparison

| | Framework (DSPy/GEPA) | Agent + Skill |
|---|---|---|
| **Search space** | Prompt string only | Entire codebase |
| **Can edit code** | No | Yes |
| **Architectural changes** | Impossible | First-class |
| **Integration** | Manual extraction | Already in codebase |
| **Failure diagnosis** | Metric goes up/down | Reads critiques, traces, logs |
| **Human oversight** | Post-hoc review | Real-time steering |
| **Negative results** | Lost | Documented |

---

## Takeaways

- **Prompt optimization frameworks work for demos and simple systems.** If you have a single-step prompt with a clean metric, DSPy with GEPA can genuinely help. Don't dismiss them entirely.

- **They break down at complexity.** The moment your system has multiple interacting prompts, architectural decisions, downstream parsers, or requires common-sense judgment about failures, algorithmic optimization hits a wall.

- **The fundamental limitation is scope.** Frameworks optimize the prompt string. But the prompt is one part of a system. The biggest wins come from architectural changes that no string optimizer would ever propose.

- **Agent skills > algorithms.** Encoding your expertise into a skill file and giving a capable agent the same tools you use is more effective, more transparent, and more flexible.

- **You still need good eval tooling.** None of this works without reliable, fast evaluation pipelines. The agent needs to be able to run experiments and see results. Invest in your eval infrastructure first.

- **The human stays in the loop.** This isn't about replacing prompt engineers. It's about amplifying what they can do. The skill file is where your expertise lives. The agent is what executes it at scale.

---

If you're spending weeks wrestling with prompt optimization frameworks and not seeing gains that stick, try the dumb thing first: write down how *you* optimize prompts, hand that document to a good AI agent, and let it rip.

---

*Zarif Aziz is the Lead AI Engineer at [Tutero](https://www.tutero.com), where he builds AI-powered educational content generation systems serving thousands of students across Australia. Connect with him on [Twitter](https://x.com/zarifaziz_) or [LinkedIn](https://www.linkedin.com/in/zarifaziz/).*
