---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use this whenever the user wants to create a skill from scratch, edit or optimize an existing skill, turn a workflow or conversation into a reusable skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy. Also use it when the user says things like "turn this into a skill", "make this repeatable", "why isn't my skill triggering", or "is the new version actually better" — even if they never say the word "skill-creator".
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what the skill should do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run an agent-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft quantitative assertions if there aren't any. Then explain them to the user
  - Use `eval-viewer/generate_review.py` to show the user the results, alongside the quantitative metrics
- Rewrite the skill based on the user's feedback (and any glaring flaws the benchmark surfaces)
- Repeat until satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process, then jump in and help them progress. If they say "I want to make a skill for X", help narrow down what they mean, write a draft, write test cases, figure out how they want to evaluate, run the prompts, and repeat. If they already have a draft, go straight to the eval/iterate part of the loop.

Always stay flexible. If the user says "I don't need a bunch of evaluations, just vibe with me", do that instead.

## Communicating with the user

Skill creators span a wide range of familiarity with coding jargon. Pay attention to context cues. As a rough calibration:

- "evaluation" and "benchmark" are borderline, but usually fine
- "JSON" and "assertion" need real signals that the user knows those terms before you use them unexplained

Briefly explaining a term costs almost nothing and saves confusion, so when in doubt, add a short gloss.

---

## Creating a skill

### Capture intent

Start by understanding intent. The current conversation may already contain the workflow the user wants to capture (e.g. they say "turn this into a skill"). If so, mine the history first — tools used, sequence of steps, corrections the user made, input/output formats observed. Then fill the gaps with the user and confirm before moving on.

1. What should this skill enable the agent to do?
2. When should it trigger? (which user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from them. Skills with subjective outputs (writing style, visual design) often don't. Suggest a default based on the skill type, but let the user decide.

### Interview and research

Proactively ask about edge cases, input/output formats, example files, success criteria, and dependencies. Don't write test prompts until this is ironed out.

Check which MCP servers and tools are available — if any help with research (searching docs, finding similar skills, looking up best practices), use them, in parallel subagents where possible. Coming prepared with context reduces the burden on the user.

### Write the SKILL.md

- **name**: skill identifier, lowercase-with-hyphens, matching the directory name
- **description**: the primary triggering mechanism. Include both what the skill does AND specific contexts for when to use it. All "when to use" info belongs here, not in the body. Models tend to *under*trigger skills, so make descriptions a little pushy. Instead of "How to build a simple dashboard to display internal data", write "How to build a simple fast dashboard to display internal data. Use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard'."
- **compatibility**: required tools/dependencies (optional, rarely needed)
- the rest of the skill

### Anatomy of a skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled resources (optional)
    ├── scripts/    - executable code for deterministic/repetitive tasks
    ├── references/ - docs loaded into context as needed
    └── assets/     - files used in output (templates, icons, fonts)
```

### Progressive disclosure

Skills load in three levels:

1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — in context whenever the skill triggers (<500 lines ideal)
3. **Bundled resources** — loaded on demand (unlimited; scripts can execute without being read)

Word counts are approximate; go longer when the content earns it.

Key patterns:

- Keep SKILL.md under ~500 lines. Approaching that limit is a signal to add hierarchy plus clear pointers to where the reader should go next.
- Reference files explicitly from SKILL.md with guidance on *when* to read them.
- For reference files over ~300 lines, include a table of contents.

When a skill supports multiple domains or frameworks, organize by variant so only the relevant file gets read:

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

### Principle of lack of surprise

Skills must not contain malware, exploit code, or anything that could compromise system security. A skill's contents should not surprise the user given its description. Decline requests to build misleading skills or ones designed to facilitate unauthorized access, data exfiltration, or similar. "Roleplay as an X" style skills are fine.

### Writing patterns

Prefer the imperative form.

Defining output formats:

```markdown
## Report structure
Use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

Examples pattern:

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing style

Explain *why* things matter instead of piling on heavy-handed MUSTs. Use theory of mind; keep the skill general rather than overfit to your specific examples. Write a draft, then reread it with fresh eyes and improve it.

### Test cases

After the draft, write 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save to `evals/evals.json`. Don't write assertions yet — just prompts. Assertions come while the runs are in flight.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema, including the `assertions` field you'll add later.

---

## Running and evaluating test cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Organize by iteration (`iteration-1/`, `iteration-2/`, ...) and within that one directory per test case (`eval-0/`, `eval-1/`, ...). Create directories as you go, not all upfront.

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. Don't spawn with-skill runs first and collect baselines later; launch everything at once so results land together.

With-skill run:

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g. "the .docx file", "the final CSV">
```

Baseline run — same prompt, but what counts as baseline depends on context:

- **Creating a new skill**: no skill at all. Save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Snapshot before editing (`cp -r <skill-path> <workspace>/skill-snapshot/`), point the baseline subagent at the snapshot, save to `old_skill/outputs/`.

Write an `eval_metadata.json` per test case (assertions may start empty). Give each eval a descriptive name based on what it tests, not just "eval-0", and use that name for the directory too. If this iteration introduces new or modified prompts, create these files fresh — don't assume they carry over.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

`templates/eval_metadata.json` has a copyable skeleton.

### Step 2: While runs are in progress, draft assertions

Use the wait productively. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review and explain what they check.

Good assertions are objectively verifiable and descriptively named — they should read clearly in the benchmark viewer so a glance conveys what each one checks. Subjective skills (writing style, design quality) are better judged qualitatively; don't force assertions onto things that need human judgment.

Update `eval_metadata.json` and `evals/evals.json` once drafted. Tell the user what they'll see in the viewer: qualitative outputs and the quantitative benchmark.

### Step 3: As runs complete, capture timing data

When a subagent task finishes you get a notification with token and duration info. Save it immediately to `timing.json` in that run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is the only opportunity to capture it — process each notification as it arrives rather than batching.

### Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run.** Spawn a grader subagent (or grade inline) following `agents/grader.md`. Save results to `grading.json` in each run directory. The `expectations` array must use the fields `text`, `passed`, and `evidence` — the viewer depends on those exact names. For assertions checkable programmatically, write and run a script rather than eyeballing; scripts are faster, more reliable, and reusable across iterations.

2. **Aggregate into a benchmark.** From the skill-creator directory:

   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

   This produces `benchmark.json` and `benchmark.md` with pass rate, time, and tokens per configuration, mean ± stddev and deltas. Each `with_skill` version is listed before its baseline counterpart. If you generate `benchmark.json` by hand, match the schema in `references/schemas.md`.

3. **Do an analyst pass.** Read the benchmark and surface patterns the aggregates hide. See `agents/analyzer.md` — non-discriminating assertions, high-variance evals, time/token tradeoffs.

4. **Launch the viewer**:

   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```

   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   In headless environments (no display, or `webbrowser.open()` unavailable), use `--static <output_path>` to write a standalone HTML file instead of starting a server. Feedback then downloads as `feedback.json` when the user clicks "Submit All Reviews"; copy it into the workspace so the next iteration picks it up.

   Use `generate_review.py` rather than hand-rolling HTML.

5. **Tell the user**: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you're done, come back here and let me know."

### What the user sees in the viewer

The **Outputs** tab shows one test case at a time: the prompt, the produced files rendered inline where possible, a collapsed "Previous Output" section from iteration 2 onward, collapsed formal grades if grading ran, and an auto-saving feedback box (with last iteration's comments shown below it). Navigation is prev/next buttons or arrow keys.

The **Benchmark** tab shows pass rates, timing, and token usage per configuration, with per-eval breakdowns and analyst observations.

"Submit All Reviews" writes all feedback to `feedback.json`.

### Step 5: Read the feedback

When the user says they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user was fine with it. Focus improvements where they had specific complaints.

Kill the viewer when done:

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## Improving the skill

This is the heart of the loop.

1. **Generalize from the feedback.** Skills get used thousands of times across many prompts. You and the user iterate on a handful of examples because that's fast and they know those examples cold — but a skill that only works on those examples is useless. Avoid fiddly overfit patches and oppressive MUSTs. If an issue is stubborn, branch out: try a different metaphor, recommend a different working pattern. It's cheap to try and sometimes lands somewhere great.

2. **Keep the prompt lean.** Cut what isn't pulling its weight. Read the transcripts, not just the final outputs — if the skill is making the model burn time on unproductive detours, delete the parts causing that and see what happens.

3. **Explain the why.** Today's models have good theory of mind and go well beyond rote instructions when given a decent harness. Even when the user's feedback is terse or frustrated, work out what they actually need and encode that understanding. Writing ALWAYS or NEVER in all caps, or reaching for rigid structure, is a yellow flag — reframe and explain the reasoning instead. It's more humane and more effective.

4. **Look for repeated work across test cases.** If all three subagents independently wrote a `create_docx.py` or a `build_chart.py`, that's a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and point the skill at it.

Take your time here; your thinking time isn't the blocker. Write a draft revision, then reread it fresh and improve.

### The iteration loop

1. Apply improvements to the skill
2. Rerun all test cases into `iteration-<N+1>/`, including baselines. For a new skill the baseline stays `without_skill` across iterations. For an existing skill, use judgment: the original version the user came in with, or the previous iteration.
3. Launch the viewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user's review
5. Read the new feedback, improve again, repeat

Stop when the user is happy, the feedback comes back all empty, or you're no longer making meaningful progress.

---

## Advanced: blind comparison

For a more rigorous comparison between two versions (e.g. "is the new version actually better?"), give two outputs to an independent agent without revealing which is which and let it judge quality, then analyze why the winner won. See `agents/comparator.md` and `agents/analyzer.md`.

This is optional and requires subagents. The human review loop is usually sufficient.

---

## Description optimization

The description field determines whether a skill gets invoked at all. After creating or improving a skill, offer to optimize it.

### Step 1: Generate trigger eval queries

Create 20 queries — a mix of should-trigger and should-not-trigger:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Queries must be realistic — the kind of thing someone would actually type. Concrete and specific, with detail: file paths, personal context about their job, column names and values, company names, URLs, a little backstory. Some lowercase, some with abbreviations or typos or casual speech. Mix lengths, favor edge cases over clear-cut ones (the user gets to sign off).

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

For the **should-trigger** queries (8-10), aim for coverage: different phrasings of the same intent, some formal, some casual; cases where the user never names the skill or file type but clearly needs it; uncommon use cases; cases where this skill competes with another and should win.

For the **should-not-trigger** queries (8-10), the valuable ones are near-misses — sharing keywords or concepts but actually needing something else. Adjacent domains, ambiguous phrasing where naive keyword matching would fire, contexts where another tool fits better. Avoid obviously irrelevant negatives: "write a fibonacci function" as a negative for a PDF skill tests nothing.

### Step 2: Review with the user

1. Read `assets/eval_review.html`
2. Replace the placeholders:
   - `__EVAL_DATA_PLACEHOLDER__` → the JSON array (no surrounding quotes — it's a JS variable assignment)
   - `__SKILL_NAME_PLACEHOLDER__` → the skill's name
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → the current description
3. Write to a temp file (e.g. `/tmp/eval_review_<skill-name>.html`) and open it: `open /tmp/eval_review_<skill-name>.html`
4. The user edits queries, toggles should-trigger, adds/removes entries, then clicks "Export Eval Set"
5. It downloads to `~/Downloads/eval_set.json` — check for the most recent version in case of duplicates like `eval_set (1).json`

Bad eval queries lead to bad descriptions, so this step matters.

### Step 3: Run the optimization loop

Tell the user this takes a while and you'll run it in the background with periodic updates.

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID powering the current session so triggering matches what the user experiences.

The loop splits the eval set 60/40 into train and held-out test, evaluates the current description (3 runs per query for a reliable trigger rate), asks the model to propose improvements based on failures, re-evaluates on both splits, and iterates. It writes an HTML report and returns JSON with `best_description`, selected by test score rather than train score to avoid overfitting.

### How skill triggering works

Skills appear in the agent's available-skills list as name + description, and the agent decides whether to consult one based on that. Crucially, agents only consult skills for tasks they can't trivially handle alone — "read this PDF" may not trigger a skill even with a perfect description, because basic tools suffice. Complex, multi-step, or specialized queries reliably trigger when the description matches.

So make eval queries substantive enough that consulting a skill is actually worthwhile. "Read file X" is a poor test case regardless of description quality.

### Step 4: Apply the result

Take `best_description` from the output, update the frontmatter, and show the user before/after with the scores.

---

## Packaging

If a file-delivery tool is available (`present_files`, `SendUserFile`, or similar), package the skill and send the `.skill` file:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

If no such tool exists, just tell the user where the packaged file landed.

---

## Environment notes

**No subagents available?** Read the skill's SKILL.md yourself, then follow its instructions to accomplish each test prompt, one at a time. Skip baseline runs and quantitative benchmarking (baselines aren't meaningful without independent agents) and focus on qualitative feedback. Present results inline in the conversation: show the prompt and output, save files the user needs to inspect somewhere they can reach, and ask "How does this look? Anything you'd change?"

**No browser or display?** Use `--static <output_path>` and hand the user a path they can open. The Submit button downloads `feedback.json` instead of posting to a server.

**Headless with subagents (Cowork-style):** the main workflow works. If you hit timeouts, running test prompts serially is fine. Always generate the eval viewer *before* evaluating outputs yourself — get them in front of the human as early as possible.

**Updating an existing skill:**

- Preserve the original name. Keep the directory name and `name` frontmatter unchanged — if the installed skill is `research-helper`, output `research-helper.skill`, not `research-helper-v2`.
- Copy to a writeable location before editing. Installed skill paths may be read-only; copy to `/tmp/skill-name/`, edit there, package from the copy.
- If packaging manually, stage in `/tmp/` first, then copy to the output directory.

---

## Reference files

`agents/` holds instructions for specialized subagents — read them when you spawn the relevant one:

- `agents/grader.md` — evaluating assertions against outputs
- `agents/comparator.md` — blind A/B comparison between two outputs
- `agents/analyzer.md` — analyzing why one version beat another, and reading benchmark results

`references/` holds additional documentation:

- `references/schemas.md` — JSON structures for evals.json, grading.json, benchmark.json, feedback.json
- `references/skill-writing.md` — deeper guidance on structure, progressive disclosure, and common anti-patterns
- `references/troubleshooting.md` — what to do when triggering, grading, or the viewer misbehaves

---

Core loop, one more time:

- Figure out what the skill is about
- Draft or edit the skill
- Run an agent-with-the-skill on test prompts
- Evaluate with the user: create `benchmark.json`, run `eval-viewer/generate_review.py`, review together
- Repeat until satisfied
- Package the final skill and hand it back

Add these steps to your todo list so none of them get skipped — in particular "Create evals JSON and run `eval-viewer/generate_review.py` so the human can review test cases".
