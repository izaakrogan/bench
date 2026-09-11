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

## 3. Exercise 1: harness

Everyone does this first.

| TEAM | TASK |
|---|---|
| | fix-code-vulnerability |
| | regex-log |
| | log-summary-date-ranges |
| | polyglot-c-py |
| | fix-code-vulnerability |

1. Find your team's task in the table.
2. Before you run anything, fill in `prediction.md` with which harness you expect to win on your task and why.
   If you're a coding agent, ask your team for the prediction rather than writing one.
3. Run these two commands, one on each of two laptops in your team so they run at the same time.
   Each runs three attempts, two at a time, and takes about 7 minutes and costs about $0.15.

   ```
   ./tb <task> claude-code
   ./tb <task> terminus-2
   ```

4. When both have finished, run `python3 collect.py` on each laptop.
   It writes `results.csv` with one row per attempt.
   Use the reward column, not the command's exit status, because Harbor exits 0 even when an attempt fails.
5. Read the transcript of every failed attempt and put each failure in one of three piles:
   it didn't attempt the right thing, it attempted the right thing and got it wrong, or the grader rejected a working solution.
6. Fill in `findings.md`.

Each attempt has its own folder, `jobs/<job>/<trial>/`, and inside it:

- `agent/trajectory.json` is the transcript of what the agent did, in the same format for both harnesses.
- `verifier/test-stdout.txt` is the grader's output, and `verifier/reward.txt` is the score.
- `exception.txt` appears only if the attempt crashed or ran out of time.

If `exception.txt` shows the attempt died before the agent did anything, it isn't a model failure, so note it separately.

In the dry run this morning, Terminus 2 on Haiku passed configure-git-webserver in about two minutes.
Claude Code on Haiku wrote a setup script and a README, never ran a command, reported success and failed the verifier, which goes in the first pile.

## 4. Keep going

You have Anthropic, OpenRouter and OpenAI keys in `~/.tb.env`.
Each of these is the same experiment with one thing changed.
Pick one, add your prediction to `prediction.md` before you run anything, then run it and add what you find to `findings.md`.

Claude Code only takes Anthropic models and Codex only takes OpenAI ones, so use Terminus 2 when you want the same harness across vendors.

### Model

Untested this morning, you're the dry run.

Keep the harness and the task, and change the model:

```
./tb <task> claude-code -m anthropic/claude-sonnet-5
./tb <task> terminus-2 -m openrouter/deepseek/<model>
```

Pick the DeepSeek model from [openrouter.ai/models](https://openrouter.ai/models).
Does a stronger or cheaper model change the result, and the cost per pass?
Cost per pass is the total `cost_usd` for the command divided by the number of attempts with a reward of 1.0.
If `cost_usd` is blank, Harbor didn't report a cost for that model, so work it out from the token columns.

### Harness on another vendor

Untested this morning, you're the dry run.

Harbor 0.22.0 has a `codex` agent, and `tb` takes it as the agent name like the others, so there's no `-a` and no `openai/` prefix on the agent.
Run it against Terminus 2 on the same OpenAI model:

```
./tb <task> codex -m openai/<model>
./tb <task> terminus-2 -m openai/<model>
```

### Skills

Untested this morning, you're the dry run.

Give Claude Code a skill you use and run the same task again, then compare it with your run from Exercise 1:

```
./tb <task> claude-code --skill <dir>
```

`<dir>` is a folder containing a `SKILL.md`, or a folder of such folders.
Most skills will show no effect here because the tasks don't call for them, and that's a result.

### Your own task

Untested this morning, you're the dry run.

Make a small task from your own work, with a test that decides whether it passed:

```
harbor tasks init <your-name>/<task-name>
```

That creates a `<task-name>` folder with `instruction.md`, `environment/Dockerfile`, `solution/solve.sh` and `tests/test.sh`, which the [Harbor task docs](https://www.harborframework.com/docs/tasks) explain.
`tb` only runs the sample tasks, so use Harbor directly, and check your own solution passes with the oracle before you try the agents:

```
harbor run -p <task-name> -a oracle -o jobs -y
harbor run -p <task-name> -a claude-code -m anthropic/claude-haiku-4-5 -k 3 -n 2 --env-file ~/.tb.env -o jobs -y
harbor run -p <task-name> -a terminus-2 -m anthropic/claude-haiku-4-5 -k 3 -n 2 --env-file ~/.tb.env -o jobs -y
```

## 5. Report back

Paste `findings.md` and `results.csv` into the [shared doc](<shared doc link>) by 5:20.

Every number you report should say which task, harness and model it came from, and how many attempts it's out of.
