# Terminal-Bench harness comparison

Same model (Claude Haiku 4.5), same Terminal-Bench tasks, two harnesses: Claude Code, and Terminus 2, which is Harbor's own neutral agent.
Does the harness change the score, and if so why?

## Setup

Start Docker Desktop and install Harbor.

```
uv tool install harbor==0.22.0
```

Keys go in `~/.tb.env`, OpenRouter and OpenAI lines only if you've got them:

```
cat > ~/.tb.env <<'EOF'
ANTHROPIC_API_KEY=your-anthropic-key
OPENROUTER_API_KEY=your-openrouter-key
OPENAI_API_KEY=your-openai-key
EOF
chmod 600 ~/.tb.env
```

Smoke test, should finish with a reward of 1.0:

```
./tb fix-code-vulnerability oracle 1 1
```

On Ubuntu tasks `tb` mounts a kernel.org apt mirror, because Ubuntu's default mirror was too slow this morning for Harbor to install the agents inside the container.

## Exercise 1: harness

| TEAM | TASK |
|---|---|
| | fix-code-vulnerability |
| | regex-log |
| | log-summary-date-ranges |
| | polyglot-c-py |
| | fix-code-vulnerability |

Run both on your task, one per laptop if you can, each is three attempts two at a time. In the dry run Claude Code took about 10 minutes and $0.75, Terminus 2 about 5 minutes and $0.15:

```
./tb <task> claude-code
./tb <task> terminus-2
```

Go by the reward Harbor prints at the end, not the exit code, it exits 0 on failed attempts.
Each attempt is in `jobs/<job>/<trial>/`, with the transcript in `agent/trajectory.json`, grader output in `verifier/test-stdout.txt`, and an `exception.txt` if it crashed or timed out.

Read every failed transcript and put it in a pile: didn't attempt the right thing, attempted it and got it wrong, or the grader rejected a working solution.

In the dry run Terminus 2 on Haiku passed configure-git-webserver in about two minutes, and Claude Code on Haiku wrote a setup script and a README, never ran a command, said it had succeeded and failed the verifier.

## Keep going

Same experiment with one thing changed.
None of these were tested this morning, you're the dry run.
Claude Code only takes Anthropic models and Codex only OpenAI ones, Terminus 2 takes all three.

### Model

```
./tb <task> claude-code -m anthropic/claude-sonnet-5
./tb <task> terminus-2 -m openrouter/deepseek/<model>
```

DeepSeek model names are on [openrouter.ai/models](https://openrouter.ai/models).
Does it change the result, and the cost per pass? Cost is in each trial's `result.json`.

### Harness on another vendor

Harbor 0.22.0 has a `codex` agent and `tb` takes it like the others:

```
./tb <task> codex -m openai/<model>
./tb <task> terminus-2 -m openai/<model>
```

### Skills

```
./tb <task> claude-code --skill <dir>
```

`<dir>` is a folder with a `SKILL.md` in it, or a folder of those.
Most skills won't show an effect because the tasks don't call for them, and that's a result.

### Your own task

`harbor tasks init <you>/<task>` scaffolds one, see the [task docs](https://www.harborframework.com/docs/tasks).
`tb` only runs the sample tasks, so use Harbor directly, oracle first:

```
harbor run -p <task> -a oracle -o jobs -y
harbor run -p <task> -a claude-code -m anthropic/claude-haiku-4-5 -k 3 -n 2 --env-file ~/.tb.env -o jobs -y
harbor run -p <task> -a terminus-2 -m anthropic/claude-haiku-4-5 -k 3 -n 2 --env-file ~/.tb.env -o jobs -y
```
