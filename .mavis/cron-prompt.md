# VCSM Auto-PR Cron Prompt

## Repo Info
- Fork: tmdeveloper007/Voice-Driven-Virtual-Customer-Success-Manager
- Upstream: ArpitaVerma16/Voice-Driven-Virtual-Customer-Success-Manager
- Workspace: /workspace/Voice-Driven-VCSM
- Token: ${GITHUB_TOKEN}

## Workflow
1. Sync fork with upstream/main
2. Fetch open issues from upstream via GitHub API
3. Check sanrishi's open PRs for file-level conflicts
4. Select up to 5 unclaimed issues with clean, regex-based fixes
5. For each: create branch, apply fix, push, create PR
6. Write summary to /workspace/.mavis/vcsm-last-run.md
7. Append PR URLs to /workspace/.mavis/vcsm-pr-log.md

## Fix Patterns Proven by Upstream
- @CrossOrigin removal
- printStackTrace → log.error
- System.out → log.info, System.err → log.error
- generic Exception → RuntimeException / specific types
- @Autowired removal + @RequiredArgsConstructor
- @NotBlank additions
- docs additions

## Constraints
- No Java/Maven in sandbox — skip compile/test
- Max 5 PRs per run
- Conflict-check files against sanrishi's 29 open PRs
- Use ${GITHUB_TOKEN} in scripts — never hardcode
