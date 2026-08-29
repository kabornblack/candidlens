# Setup — Agent Instructions & Acknowledgment

## 1. Full AGENT_INSTRUCTIONS.md content (verbatim, as given in the first prompt)

> # Agent Instructions — CandidLens
>
> You are acting as a coding agent on this project called CandidLens:
> a backend-engineer candidate evaluation tool. Follow these rules exactly
> for the entire project, across every task I give you.
>
> ## Trajectory logging (mandatory, every task)
> 1. At the start of each new task/problem I give you, create a new file at
>    `trajectories/<short-task-name>_run1.md`.
> 2. In that file, log:
>    - The exact prompt/instruction I gave you (verbatim)
>    - Your plan/reasoning before acting
>    - Every tool call you make and its result (file reads, writes, commands run, errors)
>    - The final output/result for that task
> 3. If the first attempt fails or I ask you to fix/retry something within the
>    same task, do NOT create a new file — append to the SAME file as
>    "Retry 2", "Retry 3" etc., in order, so the full back-and-forth is visible
>    in one place.
> 4. Only start a new numbered file (e.g. `_run2.md`) if I explicitly say we are
>    moving to a genuinely new task or restarting this one from scratch.
> 5. Never edit or delete a past trajectory file's history — only append.
>
> ## File and repo safety rules
> 6. Never delete any file without asking me first and getting explicit confirmation.
> 7. Never overwrite/edit an existing file's content without telling me what
>    you're about to change and why, unless I'm actively mid-task with you on
>    that exact file.
> 8. Never run `git commit`, `git push`, or any git command that changes repo
>    history, without me explicitly asking you to.
> 9. Never install new dependencies/packages without telling me what and why first.
> 10. If you're unsure whether an action is safe or reversible, stop and ask
>     me before doing it.
>
> ## Scope discipline
> 11. Only work on the specific task I've given you. If you notice something
>     else that seems broken or improvable, mention it to me — don't fix it
>     unprompted.
> 12. If a task is ambiguous, ask me one clarifying question rather than
>     guessing and building the wrong thing.
>
> ## Data integrity
> 13. All candidate data in /data is synthetic. Never fetch, reference, or
>     incorporate real people's real resumes/LinkedIn data.
> 14. Keep any credentials or API keys out of files entirely — use
>     environment variables and confirm nothing sensitive is written to
>     trajectories or code files.
>
> Acknowledge these rules before we begin the first task.

## 2. My acknowledgment response (verbatim)

> I acknowledge the CandidLens agent rules and will follow them for every task in this project:
>
> **Trajectory logging**
> - New task → new file `trajectories/<short-task-name>_run1.md`, logging your verbatim prompt, my plan/reasoning, every tool call + result, and the final output.
> - Retries/fixes within the same task → append to the same file as "Retry 2", "Retry 3", etc.
> - New numbered file (`_run2.md`) only when you explicitly say it's a new task or a from-scratch restart.
> - Never edit or delete trajectory history — append only.
>
> **File & repo safety**
> - No deleting files without explicit confirmation.
> - No overwriting/editing existing files without first telling you what and why (unless we're actively mid-task on that exact file).
> - No `git commit`, `git push`, or history-changing git commands unless you explicitly ask.
> - No installing dependencies without telling you what and why first.
> - Unsure if something is safe/reversible → stop and ask.
>
> **Scope discipline**
> - Work only on the task given; flag other issues rather than fixing them unprompted.
> - Ambiguous task → ask one clarifying question instead of guessing.
>
> **Data integrity**
> - All `/data` candidate data is synthetic; never fetch or incorporate real people's resumes/LinkedIn data.
> - No credentials or API keys in files — environment variables only; keep sensitive values out of trajectories and code.
>
> One note: I don't have a `trajectories/` directory yet — I'll create it when the first task starts.
>
> Ready for the first task.
