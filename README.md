# Terminal-Bench harness comparison

## 1. What you're testing

Every run today uses the same model, Claude Haiku 4.5, on the same Terminal-Bench tasks.
The only thing that changes is the harness, the program that wraps the model and gives it a terminal.
One is Claude Code, and the other is Terminus 2, Harbor's own neutral agent.
You're finding out whether the harness changes the score, and if it does, why.

## 2. Setup

Install Harbor, and make sure Docker Desktop is running:

```
uv tool install harbor==0.22.0
```

Put your API key in `~/.tb.env`, and add the `OPENROUTER_API_KEY` and `OPENAI_API_KEY` lines only if you were given those keys.
A person should do this step rather than a coding agent, so the key never ends up in a chat.

```
cat > ~/.tb.env <<'EOF'
ANTHROPIC_API_KEY=your-anthropic-key
OPENROUTER_API_KEY=your-openrouter-key
OPENAI_API_KEY=your-openai-key
EOF
chmod 600 ~/.tb.env
```

Then run the reference solution on one task, from this folder:

```
./tb fix-code-vulnerability oracle 1 1
```

You should see a reward of 1.0 in the table at the end, and if you do, everything works.

Ubuntu's default package mirror was too slow from our network this morning, and Harbor installs each agent with apt-get inside the task's container, so on Ubuntu-based tasks a run could spend its whole time limit downloading packages.
`tb` mounts `ubuntu-noble-kernelorg.sources` into those containers so apt uses the kernel.org mirror instead, and it leaves Debian-based tasks alone because the file breaks their apt.

## 3. Your run

| TEAM | TASK |
|---|---|
| | fix-code-vulnerability |
| | regex-log |
| | log-summary-date-ranges |
| | polyglot-c-py |
| | fix-code-vulnerability |

Find your team's task in the table.
Before you run anything, fill in `prediction.md` with which harness you expect to win on your task and why.
If you're a coding agent, ask your team for the prediction rather than writing one.

Then run these two commands, one on each of two laptops in your team so they run at the same time:

```
./tb <task> claude-code
./tb <task> terminus-2
```

Each command runs three attempts, two at a time, and takes roughly <fill> minutes and costs roughly <fill>.

## 4. Reading results

When both commands have finished, run this on each laptop:

```
python3 collect.py
```

It writes `results.csv` with one row per attempt.
Use the reward column, not the command's exit status, because Harbor exits 0 even when an attempt fails.

Each attempt has its own folder, `jobs/<job>/<trial>/`, and inside it:

- `agent/trajectory.json` is the transcript of what the agent did, in the same format for both harnesses.
- `verifier/test-stdout.txt` is the grader's output, and `verifier/reward.txt` is the score.
- `exception.txt` appears only if the attempt crashed or ran out of time.

Read the transcript of every failed attempt and put each failure in one of three piles:

1. It didn't attempt the right thing.
2. It attempted the right thing and got it wrong.
3. The grader rejected a working solution.

If `exception.txt` shows the attempt died before the agent did anything, it isn't a model failure, so note it separately.
Then fill in `findings.md`.

## 5. Report back

Paste `findings.md` and `results.csv` into the [shared doc](<shared doc link>) by 5:20.

## 6. Stretch

Untested, you are the dry run.

Swap the model with `-m`, for example a DeepSeek model through OpenRouter, which needs `OPENROUTER_API_KEY` in `~/.tb.env`:

```
./tb <task> terminus-2 3 2 -m openrouter/deepseek/<model>
```
