# Article Context Dump: Prompt Optimization Frameworks vs Agents

This file contains all context provided by Zarif during the writing of `prompt-optimization-frameworks-vs-agents.md`. Another AI agent can use this to continue editing, refining, or restructuring the article.

---

## Author

- **Name**: Zarif Aziz
- **Role**: Lead AI Engineer at Tutero
- **Twitter**: @zarifaziz_
- **LinkedIn**: https://www.linkedin.com/in/zarifaziz/
- **Location**: Sydney, Australia

## Company

- **Tutero**: Ed-tech company, AI-powered tutoring, thousands of students across Australia
- AI pipeline generates lesson plan components: warm-up questions, scaffolded tasks, application problems, exit tickets, misconception nodes, thought sparkers, warm-up with context
- 7+ content types, each with own generation + scoring prompts
- Pipeline: Generate N candidates → Select & Refine → LLM Judge (PASS/FAIL + critique)
- Production stack includes Go service downstream that parses XML tags from prompt outputs
- Uses Mustache templates for prompt rendering
- Fast models (~3500 TPS via Cerebras)

## IP / Sensitivity Guidelines

- **OK to share**: Tutero name, Zarif's role, pipeline architecture, skill file excerpts, general approach, experiment results/numbers
- **NOT OK to share**: Specific judge templates, proprietary prompt text, specific scorer criteria, internal code details that would constitute trade secrets
- The article should be something Tutero's CPO/CEO wouldn't be upset about being published on Medium

---

## Core Thesis

Prompt optimization frameworks (DSPy, GEPA, MIPRO) are only useful for simple systems and demos. For complex production systems, they fail because:

1. They can only see/edit the prompt string — no visibility into code, pipeline, response models, downstream parsers
2. They can't make architectural changes (the biggest wins come from structural changes, not wording)
3. Optimized prompts don't transfer cleanly back to production (replication gap)

The better approach: give a capable AI agent a "skill file" (markdown encoding your expert process) with full codebase access and let it operate like a prompt engineer would. This is part of a broader "get out of the way" pattern in AI tooling.

## Key Theme: "Get Out of the Way"

The article connects to a broader pattern:
- **Amp's "How to Build an Agent"** (https://ampcode.com/notes/how-to-build-an-agent): "An agent is just an LLM, a loop, and enough tokens." Built in <400 lines of Go. No hidden complexity.
- **Pi coding agent** by Mario Zechner (https://mariozechner.at/posts/2025-11-30-pi-coding-agent/): 4 tools, <1000 token system prompt, "if I don't need it, it won't be built", competed with 10x more complex agents
- **Amp's "Agents for the Agent"** (https://ampcode.com/notes/agents-for-the-agent): They noticed Claude naturally wanted to delegate to subagents, so they enabled it rather than constraining it
- The shared principle: frameworks constrain the LLM, but the LLM is already smart — give it tools and context, then get out of the way
- **Hamel Husain's evals-skills** (https://github.com/hamelsmu/evals-skills): Open-source skills for AI agents to build evals, audit pipelines, analyze errors, write judge prompts. Worked with 50+ companies on LLM evals. Same philosophy — encode expert knowledge into skills, give agent tools, let it work. Tweet: https://x.com/HamelHusain/status/2028894099483578872

## Zarif's Twitter Post (Jan 27, 2026)

Tweet: https://x.com/zarifaziz_/status/1883708048505917893
Content: "I've tried prompt automation tools like DSPY/GEPA and happy to say that prompt engineering is still well and truly alive. Most demos of how 'prompt engineering is dead' is good for toy demos and selling products, but doesn't work at a high complexity level."
Quote-tweeting Mike Taylor (@hammer_mt) who referenced Sam Altman saying we won't be doing prompt engineering in 5 years.

---

## DSPy Experiment Details

### What was built
- Two-step pipeline: judge optimization → generator optimization
- Used GEPA (Genetic Pareto Optimization) specifically — consistently outperforms MIPRO
- Judge optimization: up to 300 GEPA iterations, stratified train/test splits, aligning with human labels
- Generator optimization: up to 50 GEPA iterations, using calibrated judge as feedback
- Anti-memorization safeguards (system prompt + custom instruction proposers)
- W&B tracking, checkpointing, graceful interrupt handling
- Models: Cerebras GPT-OSS-120B (student), GPT-5.2 (teacher)
- Training data: 200 synthetic examples, holdout: 100 examples

### Results / Problems
- Application score: 43% → 53% after DSPy run
- But judge became miscalibrated — too harsh, failing on trivial misunderstandings, not applying common sense
- "DSPY creates a very harsh judge but also a stupid judge that fails based on stupid misunderstandings"
- Judge was: marking creative scenarios as "not real", ignoring fields prompt said to ignore, being overly literal about age-level wording, penalizing chain-of-thought fields even though prompt says to ignore them
- **Replication gap**: DSPy internal evaluator said 73%, production eval pipeline said 64%. Same prompt, same data.
- Even after getting 78% on a second run (1hr 3min), copying the prompt to production gave 64% again
- With user prompt placement, dropped to 38% — "so weird"
- Had to cancel a "heavy" run — too long and logs didn't look good
- Scores were inconsistent: 45%, then 63%, then 60%, then 55% across runs with same config

### Slack Discussion Context (Dec 6, 2025)
- Zarif shared GEPA optimizer usage with colleague Richard Mathieson
- Richard asked about trying MIPROv2 — Zarif said GEPA consistently outperforms MIPRO
- Dataset was 130 examples, with working/trusted judge the dataset can be "technically infinite"
- Used only instruction prompt optimizer (drops few-shot examples), then added few-shot manually in post

### Notion Notes Context
- "DSPY boosts scores but still makes avoidable common-sense mistakes in the final prompt"
- "Still have to correct issues after 'optimisation' (e.g., over-harshness, false FAILs, conciseness misunderstandings), so the final prompt isn't plug-and-play"
- Multiple optimization runs in progress with different configs (max_optimization_evals=30/15, reflection_minibatch_size=15/25)
- gpt-5.1 as judge was too slow; replicated performance using Cerebras + 3-rep consensus

---

## Agent Skills Details

### Source Location
Skills folder: `/Users/zariftutero/Coding/metarepo/backend/library/prompting/.claude/skills/`

### Skills Available
1. **optimizing-generator-prompts/SKILL.md** — Optimize generator prompts using eval + error analysis pipelines
2. **optimizing-judge-prompts/SKILL.md** — Iteratively refine LLM judge prompts for model-human agreement
3. **running-prompt-experiment/SKILL.md** — Run controlled prompt architecture experiments in isolated git worktrees
4. **ensemble-select-refine/SKILL.md** — Apply ensemble + select & refine pattern to node types
5. Reference docs: calibration-phrases.md, prompt-structure.md

### Key Skill Design Principles
- Encode expert judgment, not algorithms
- Tell the agent the goal, philosophy, data locations, tools, and scope
- Include triage process: inspect 3-5 failures manually before batch analysis
- Early exit rule: if judge is wrong, stop and escalate (don't optimize against broken judge)
- Greedy fixing: act on obvious patterns immediately
- Experimentation mindset: consider beyond prompt edits (ensemble, chain-of-thought, prompt chains, inference compute scaling)
- Variance awareness: only trust >4% improvements on 50 samples
- Compaction protocol: summary format for when context gets long

### Judge Skill Specifics
- Decision tree for diagnosing disagreements (too lenient / too strict / unclear criteria)
- Train/test discipline (iterate on training only, test for final validation)
- Priority order: refine criteria → adjust calibration → replace examples (last resort)
- Smart plateau detection: stop at <2% improvement only if agreement ≥75%
- Target: ≥80% agreement on training set

### Experiment Skill Specifics
- Creates isolated git worktrees for experiments
- Experiment patterns: Plan-Then-Generate (Blueprint), Design Brief (Per-Candidate Planning), Generate-Critique-Revise
- Function signatures are sacred (eval pipeline depends on them)
- Mustache templates are sacred
- Parallelization via teams (one agent per node type)

---

## Agent-Driven Results

### Warm Up With Context
- Training baseline: 24%, after agent: 44-56% (+20-32pp)
- Holdout baseline: 40%, after agent: 60% (+20pp)
- 7 distinct changes: named prerequisite fields with model_validator, context reference injection, explicit ALL-THREE-questions context check, ≤8 word sentence rule for PrepTo2, yes/no ban, per-level prerequisite reminders in questionReasoning, prerequisite diversity across candidates
- Agent identified ~3% of failures were judge miscalibration (scorer fix needed, not generator)

### Scaffolded Question (Ensemble Experiment)
- Baseline (pre-optimization): 62%
- Baseline (committed v7.1): 70%
- Independent gen (parallel): 80% training, 79% holdout
- Key change: architectural — "1 call → 3 entangled candidates" to "3 parallel calls → 3 independent candidates"
- Generation prompt simplified from "generate 3 candidates" to "generate 1 candidate"
- Task function: 3 parallel ThreadPoolExecutor calls instead of 1
- Why it works: candidate deentanglement (independent calls = truly diverse outputs), simpler task (1 candidate easier than 3), no time penalty (parallel execution)
- Failed approaches documented: 5 candidates in 1 call (56%), end-of-prompt reminder (66%, regression), all text-based additions from prev session (all regressed — "prompt at local optimum for text changes")

### Across All Node Types (from Slack Feb 11, 2026)
- Misconception: 65% → 83% (huge success)
- Exit Ticket: 10% → 36.3% (big success)
- Scaffolded: 35% → 90% (huge)
- Thought Sparker: 84 → 91%
- Application: 53% → 63%
- Warm Up: 53% → 83%
- Warm Up With Context: 37 → 62% (huge)

### Slack Context (Feb 11, 2026)
- "LFG team. We've had huge prompt improvements across the board"
- "Ensemble method experiments have been very successful"
- "I'm very bullish on increasing the inference time compute / adding chains to improve our output quality"
- "We're also closer to fully Automated prompt engineering taking over"
- Skills give the agent: basic knowledge of tools in repo, freedom to make architectural changes (not just prompt string changes)
- "Claude Opus is great at using the codebase to make system adjustments, running experiments, and verifying prompt improvements"
- Example: Warm Up With Context 40%→60%, Scaffolded node reaching plateau with sequential ensemble → agent implemented parallel ensemble → 60→70%

---

## Writing Style Requirements

Based on analysis of Zarif's existing Medium articles:
- **Tone**: Casual-authoritative, first person, conversational but credible
- **Structure**: Problem/hook → context with disclaimer → real experience (warts and all) → actionable takeaways
- **Paragraphs**: Short, scannable
- **Headers**: Action-oriented or narrative-driven
- **Anecdotes**: High density, used to anchor technical points
- **Code**: Used as teaching tool, with explanatory context before/after
- **Closing**: Actionable takeaways or reflective questions
- **Engagement**: Direct address to reader, relatable frustrations, transparent about scope
- **No emojis in article text** (unless user explicitly requests)

### Existing Articles (for style reference)
- `/Users/zariftutero/Coding/personal/medium-articles/custom-stable-diffusion.txt`
- `/Users/zariftutero/Coding/personal/medium-articles/data-science-reflections.txt`
- `/Users/zariftutero/Coding/personal/medium-articles/bridging-the-gap-python.txt`
- `/Users/zariftutero/Coding/personal/medium-articles/medium-article-storage-cleanup.md`

---

## Editorial Decisions Made

1. **Tutero named openly** — authority/credibility is important
2. **Skill file excerpts shared liberally** — Zarif said "go with the liberal sharing approach and then I can review and remove things if we're oversharing"
3. **Claude/Anthropic references softened** — to avoid reading like a sponsored post. The thesis is "agent + skill" generically.
4. **"The Moment It Clicked" section added** — narrative transition between DSPy failure and skill discovery (the afternoon of asking the agent to look at failures)
5. **Trimmed from ~4300 to ~3700 words** — cut redundant diagrams, trimmed skill excerpts from 7 code blocks to 3, removed standalone comparison section
6. **Comparison table kept, mermaid comparison diagram cut** — tables scan faster on Medium
7. **Twitter post woven into intro** — creates narrative arc with Sam Altman "prompt engineering is dead" framing
8. **Image/screenshot placeholders throughout** — Zarif will fill these in with actual screenshots

## Image Placeholders in Article

The article contains these image placeholders that need real screenshots:
1. Slack discussion about DSPy results and judge miscalibration
2. Terminal showing DSPy 73% vs production eval 64%
3. Agent results summary for sequential vs parallel comparison
4. Agent optimization summary for WarmUpWithContext
5. Agent final results showing parallel generation architecture
6. Slack message showing all-node-types improvement table
7. Slack message "We're also closer to fully Automated prompt engineering taking over"

---

## Source Files for Reference

- **DSPy scripts**: `/Users/zariftutero/Coding/metarepo/backend/library/prompting/scripts/run_generator_optimization.py` and `run_judge_optimization.py`
- **DSPy core**: `/Users/zariftutero/Coding/metarepo/backend/library/prompting/src/prompting/core/dspy/`
- **DSPy services**: `/Users/zariftutero/Coding/metarepo/backend/library/prompting/src/prompting/services/pipeline/dspy_optimizer.py`
- **Skills**: `/Users/zariftutero/Coding/metarepo/backend/library/prompting/.claude/skills/`
- **Experiments**: `/Users/zariftutero/Coding/metarepo/backend/library/prompting/data/experiments/`
- **Task files**: `/Users/zariftutero/Coding/metarepo/backend/library/prompting/src/prompting/tasks/lesson_plan/`
- **Scorer files**: `/Users/zariftutero/Coding/metarepo/backend/library/prompting/src/prompting/scorers/`

---

## Audience / Distribution Plan

- **Primary**: Medium article (full length, ~3700 words)
- **Secondary**: LinkedIn post (condensed 400-word version linking to Medium)
- **Tertiary**: Twitter/X post linking to article
- Target audience: AI engineers, prompt engineers, people building LLM systems in production
- The article should spark productive debate (not trash DSPy, but show where it breaks down)
- Risk to watch: article could read like a Claude ad if not careful — keep thesis generic ("agent + skill" not "use Claude specifically")
