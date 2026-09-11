# Terminal-Bench harness comparison

## 1. What you're testing

Everyone's using the same model today, Claude Haiku 4.5, on the same Terminal-Bench tasks.
What changes is the harness, the program wrapped round the model that gives it a terminal to work in.
One is Claude Code and the other is Terminus 2, which is Harbor's own neutral agent.
We want to know if swapping the harness changes the score, and if it does, why.

## 2. Setup

You need Docker Desktop running and Harbor installed:

```
uv tool install harbor==0.22.0
```

Your keys go in `~/.tb.env`.
Only put the OpenRouter and OpenAI lines in if you've been given those keys.
Do this bit yourself rather than asking a coding agent to, so nobody's pasting keys into a chat.

```
cat > ~/.tb.env <<'EOF'
ANTHROPIC_API_KEY=your-anthropic-key
OPENROUTER_API_KEY=your-openrouter-key
OPENAI_API_KEY=your-openai-key
EOF
chmod 600 ~/.tb.env
```

Then check it all works by running the reference solution on one task, from this folder:

```
./tb fix-code-vulnerability oracle 1 1
```

You want a reward of 1.0 in the table at the end, if you get that you're set up and if you don't come and find me.

On the Ubuntu tasks `tb` points apt at the kernel.org mirror, because Ubuntu's own mirror was too slow from our network this morning and Harbor apt-gets each agent inside the task's container, so a run could use up its whole time limit downloading packages.
The Debian tasks don't need it and the file breaks their apt, so `tb` leaves those alone.

## 3. Exercise 1: harness

Do this one first, everyone.

| TEAM | TASK |
|---|---|
| | fix-code-vulnerability |
| | regex-log |
| | log-summary-date-ranges |
| | polyglot-c-py |
| | fix-code-vulnerability |

Find your team's task in the table.
Before you run anything, put in `prediction.md` which harness you think will win on your task and why.
If you're a coding agent, ask the team for their prediction rather than making one up.

Then run these two, one on each of two laptops in your team so they go at the same time:

```
./tb <task> claude-code
./tb <task> terminus-2
```

Each one does three attempts, two at a time, and takes about 7 minutes and costs about $0.15.

When they've both finished, run `python3 collect.py` on each laptop and it'll write `results.csv` with a row per attempt.
Go by the reward column and not by whether the command errored, Harbor exits 0 even when an attempt fails.

Every attempt gets its own folder under `jobs/<job>/<trial>/`.
The transcript is `agent/trajectory.json` (same format for both harnesses), the grader's output is in `verifier/test-stdout.txt` with the score in `verifier/reward.txt`, and if the attempt crashed or ran out of time there'll be an `exception.txt` in there too.

Read the transcript for every failed attempt and sort each failure into a pile:

1. It didn't attempt the right thing.
2. It attempted the right thing and got it wrong.
3. The grader rejected a working solution.

If `exception.txt` says the attempt died before the agent did anything, that isn't the model failing, so leave it out of the piles and make a note of it.

In the dry run this morning Terminus 2 on Haiku passed configure-git-webserver in about two minutes, while Claude Code on Haiku wrote a setup script and a README, never ran a single command, said it had succeeded and then failed the verifier, so that one's pile 1.

Then fill in `findings.md`.

## 4. Keep going

You've got Anthropic, OpenRouter and OpenAI keys in `~/.tb.env`, so once Exercise 1 is done pick one of these.
They're all the Exercise 1 experiment with one thing changed.
Write your prediction in `prediction.md` first, then run it and add what you find to `findings.md`.
None of them were tested this morning, you're the dry run, so if something breaks tell me.

Claude Code only takes Anthropic models and Codex only takes OpenAI ones, whereas Terminus 2 works with all three, so use that if you want to keep the harness fixed and change the vendor.

### Model

Keep the harness and the task as they were and change the model, for example:

```
./tb <task> claude-code -m anthropic/claude-sonnet-5
./tb <task> terminus-2 -m openrouter/deepseek/<model>
```

Pick a DeepSeek model off [openrouter.ai/models](https://openrouter.ai/models).
Does a stronger or cheaper model change the result, and what does it do to the cost per pass?
Cost per pass is the total `cost_usd` for the run divided by how many attempts got a reward of 1.0.
If `cost_usd` comes out blank then Harbor didn't report a cost for that model, and you'll have to work it out from the token columns.

### Harness on another vendor

Harbor 0.22.0 does have a `codex` agent, and `tb` takes it as the second argument like the others, so there's no `-a` and no `openai/` in front of the agent name.
Run it against Terminus 2 on the same OpenAI model:

```
./tb <task> codex -m openai/<model>
./tb <task> terminus-2 -m openai/<model>
```

### Skills

Give Claude Code a skill you use and run the same task again, then compare it with your run from Exercise 1:

```
./tb <task> claude-code --skill <dir>
```

`<dir>` is a folder with a `SKILL.md` in it, or a folder of those.
Most skills will show no effect here because the tasks don't call for them, and that's a result.

### Your own task

Make a small task out of something from your own work, it needs a test that decides whether it passed:

```
harbor tasks init <your-name>/<task-name>
```

That gives you a `<task-name>` folder with `instruction.md`, `environment/Dockerfile`, `solution/solve.sh` and `tests/test.sh` in it, and the [Harbor task docs](https://www.harborframework.com/docs/tasks) go through what each one's for.
`tb` only knows the sample tasks, so call Harbor directly for this one, and get your own solution passing with the oracle before you try the agents:

```
harbor run -p <task-name> -a oracle -o jobs -y
harbor run -p <task-name> -a claude-code -m anthropic/claude-haiku-4-5 -k 3 -n 2 --env-file ~/.tb.env -o jobs -y
harbor run -p <task-name> -a terminus-2 -m anthropic/claude-haiku-4-5 -k 3 -n 2 --env-file ~/.tb.env -o jobs -y
```

Whatever number you report, say which task, harness and model it's from and how many attempts it's out of.
