#!/usr/bin/env python3
"""
VCSM Auto-PR Orchestrator
Fork: tmdeveloper007/Voice-Driven-Virtual-Customer-Success-Manager
Upstream: ArpitaVerma16/Voice-Driven-Virtual-Customer-Success-Manager
Max 5 PRs per run. No Java — regex-based targeted fixes only.
"""
import os, sys, json, subprocess, time, requests

REPO_DIR = "/workspace/Voice-Driven-VCSM"
os.chdir(REPO_DIR)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json", "User-Agent": "mavis-bot/1.0"}
FORK_OWNER = "tmdeveloper007"
UPSTREAM_OWNER = "ArpitaVerma16"
REPO_NAME = "Voice-Driven-Virtual-Customer-Success-Manager"
FORK_API = f"https://api.github.com/repos/{FORK_OWNER}/{REPO_NAME}"
MAX_PRS = 5


def run_cmd(cmd, check=True, cwd=REPO_DIR):
    print(f"  $ {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if check and r.returncode != 0:
        print(f"  [!] Failed: {r.stderr.strip()}")
        raise Exception(f"Command failed: {' '.join(cmd)}")
    return r.stdout.strip()


def gh_api(url, method="GET", data=None):
    h = dict(GITHUB_HEADERS)
    h["Authorization"] = f"token {GITHUB_TOKEN}"
    resp = requests.request(method, url, headers=h,
                           json=data if method not in ("GET", "HEAD") else None,
                           params=data if method in ("GET", "HEAD") else None)
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, {"raw": resp.text[:500]}


def file_edit(filepath, replacements):
    """Apply list of (old, new) 2-tuples to a file."""
    path = os.path.join(REPO_DIR, filepath)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    for old, new in replacements:
        if old not in content:
            print(f"  [!] Pattern not found in {filepath}: {repr(old[:80])}")
        content = content.replace(old, new)
    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [+] Edited {filepath}")
        return True
    print(f"  [-] No changes to {filepath}")
    return False


# ─── PR definitions ────────────────────────────────────────────────────────────
# Each replacement is (OLD, NEW) — a 2-tuple. All strings on one logical line.

PR_DEFINITIONS = [

    # PR 1: AnalyticsService — remove redundant @Autowired constructor
    {
        "branch": "fix/analytics-remove-redundant-autowired-constructor",
        "title": "refactor: remove redundant @Autowired constructor in AnalyticsService",
        "body": (
            "## What\n"
            "AnalyticsService carries both `@lombok.RequiredArgsConstructor` and an explicit "
            "`@Autowired` constructor with the same signature. The explicit constructor is "
            "redundant in Spring 4.3+.\n\n"
            "## Changes\n"
            "- Remove the redundant `@Autowired` annotated constructor — "
            "Lombok's `@RequiredArgsConstructor` already handles constructor injection for the two `final` fields.\n\n"
            "## Why\n"
            "Eliminates duplicate wiring logic. Spring automatically injects single-constructor "
            "beans without requiring `@Autowired`.\n"
        ),
        "files": {
            "src/main/java/com/vcsm/service/AnalyticsService.java": [
                (
                    "    @Autowired\n    public AnalyticsService(SentimentAnalysisRepository sentimentRepository, VoiceCommandRepository voiceCommandRepository) {\n        this.sentimentRepository = sentimentRepository;\n        this.voiceCommandRepository = voiceCommandRepository;\n    }\n",
                    "",
                ),
            ],
        },
    },

    # PR 2: OmnidimService — remove @Autowired fields + fix ResponseEntity return bugs + missing brace
    {
        "branch": "fix/omnidim-fix-autowired-responseentity-missing-brace",
        "title": "fix: OmnidimService — remove redundant Autowired fields, fix ResponseEntity returns, add missing closing brace",
        "body": (
            "## What\n"
            "OmnidimService has three separate issues:\n\n"
            "1. **Redundant field `@Autowired`** — the class uses `@RequiredArgsConstructor` (Lombok) "
            "for constructor injection, but `complaintRepository` and `eventService` are marked "
            "`@Autowired` on the field, making the annotation redundant.\n\n"
            "2. **`detectIntent()` returns `ResponseEntity<String>` instead of `String`** — "
            "methods like `return org.springframework.http.ResponseEntity.ok(\"BOOK_VENUE\")` "
            "return `ResponseEntity<String>` but the method return type is `String`. "
            "This causes `.toString()` to be called on the ResponseEntity, producing "
            'e.g. `"org.springframework.http.HttpEntity@1234..."`.\n\n'
            "3. **Missing closing brace** — `getRecentCommands(Boolean success)` is missing a `}` "
            "before `private String handleEventBooking`, causing a compilation error.\n\n"
            "## Changes\n"
            "- Remove `@Autowired` from `complaintRepository` and `eventService` fields\n"
            "- Replace all `return org.springframework.http.ResponseEntity.ok(\"...\")` with plain `return \"...\"`\n"
            "- Add missing `}` after `return voiceCommandRepository.findByProcessedOrderByCreatedAtDesc(success);`\n\n"
            "## Why\n"
            "Fixes compilation error and restores correct voice-command response strings.\n"
        ),
        "files": {
            "src/main/java/com/vcsm/service/OmnidimService.java": [
                # Remove redundant @Autowired fields
                ("    @Autowired\n    private com.vcsm.repository.ComplaintRepository complaintRepository;", "    private final com.vcsm.repository.ComplaintRepository complaintRepository;"),
                ("    @Autowired\n    private EventService eventService;", "    private final EventService eventService;"),
                # Fix ResponseEntity returns in detectIntent
                ('            return org.springframework.http.ResponseEntity.ok("BOOK_VENUE");', '            return "BOOK_VENUE";'),
                ('        if (t.contains("status") || t.contains("check") || t.contains("my complaint")) return org.springframework.http.ResponseEntity.ok("CHECK_COMPLAINT");', '        if (t.contains("status") || t.contains("check") || t.contains("my complaint")) return "CHECK_COMPLAINT";'),
                ('                || t.contains("security") || t.contains("parking")) return org.springframework.http.ResponseEntity.ok("FILE_COMPLAINT");', '                || t.contains("security") || t.contains("parking")) return "FILE_COMPLAINT";'),
                ('                || t.contains("un-register") || t.contains("unregister")) return org.springframework.http.ResponseEntity.ok("CANCEL_REGISTRATION");', '                || t.contains("un-register") || t.contains("unregister")) return "CANCEL_REGISTRATION";'),
                ('                || t.contains("activity")) return org.springframework.http.ResponseEntity.ok("EVENT_QUERY");', '                || t.contains("activity")) return "EVENT_QUERY";'),
                ('                || t.contains("summary")) return org.springframework.http.ResponseEntity.ok("ANALYTICS");', '                || t.contains("summary")) return "ANALYTICS";'),
                # Fix in handleCancelRegistration
                ('            return org.springframework.http.ResponseEntity.ok("User not found. Please log in first.");', '            return "User not found. Please log in first.";'),
                ('            return org.springframework.http.ResponseEntity.ok("You are not registered for any upcoming events.");', '            return "You are not registered for any upcoming events.";'),
                ('            return org.springframework.http.ResponseEntity.ok("Which event registration would you like to cancel? Please specify the event name.");', '            return "Which event registration would you like to cancel? Please specify the event name.";'),
                # Fix in handleEventQuery
                ('        if (upcoming.isEmpty()) return org.springframework.http.ResponseEntity.ok("No upcoming events right now. Check back soon!");', '        if (upcoming.isEmpty()) return "No upcoming events right now. Check back soon!";'),
                # Fix in handleEventBooking
                ('            return org.springframework.http.ResponseEntity.ok("Unable to book event: user session not found.");', '            return "Unable to book event: user session not found.";'),
                ("            return org.springframework.http.ResponseEntity.ok(\"Sorry, I couldn't find an event matching that description. Please try specifying the exact event name.\");", "            return \"Sorry, I couldn't find an event matching that description. Please try specifying the exact event name.\";"),
                ("            return org.springframework.http.ResponseEntity.ok(\"Success! You have been registered for \" + updatedEvent.getName() + \". A confirmation email with your ticket check-in QR code has been sent to \" + user.getEmail() + \".\");", "            return \"Success! You have been registered for \" + updatedEvent.getName() + \". A confirmation email with your ticket check-in QR code has been sent to \" + user.getEmail() + \".\";"),
                # Fix missing closing brace
                ("        return voiceCommandRepository.findByProcessedOrderByCreatedAtDesc(success);\n    private String handleEventBooking(String t) {", "        return voiceCommandRepository.findByProcessedOrderByCreatedAtDesc(success);\n    }\n\n    private String handleEventBooking(String t) {"),
            ],
        },
    },

    # PR 3: ExperimentController — convert field injection to constructor injection
    {
        "branch": "fix/experiment-controller-constructor-injection",
        "title": "refactor: ExperimentController — convert field injection to constructor injection",
        "body": (
            "## What\n"
            "ExperimentController uses field injection (`@Autowired private ExperimentService experimentService`) "
            "which is less testable and harder to reason about than constructor injection.\n\n"
            "## Changes\n"
            "- Add `@lombok.RequiredArgsConstructor` to generate the constructor\n"
            "- Remove `@Autowired` annotation from the field\n"
            "- Change field from `private ExperimentService experimentService` to `private final ExperimentService experimentService`\n\n"
            "## Why\n"
            "Constructor injection makes dependencies explicit, enables immutability (`final`), "
            "and improves testability. Spring automatically injects beans when a class has a single constructor.\n"
        ),
        "files": {
            "src/main/java/com/vcsm/abtesting/ExperimentController.java": [
                ("import org.springframework.beans.factory.annotation.Autowired;\n", ""),
                ("    @Autowired\n    private ExperimentService experimentService;", "    @lombok.RequiredArgsConstructor\n    private final ExperimentService experimentService;"),
            ],
        },
    },

    # PR 4: WebController — fix ResponseEntity return type bugs in @Controller methods
    {
        "branch": "fix/webcontroller-return-types",
        "title": "fix: WebController — fix String return values in @Controller methods",
        "body": (
            "## What\n"
            "Several `@GetMapping` methods in WebController return `org.springframework.http.ResponseEntity.ok(\"...\")` "
            "but the method return type is `String`. This causes Spring MVC to call `.toString()` on the "
            "ResponseEntity, returning a string like `\"org.springframework.http.HttpEntity@7f4...\"` instead "
            "of the intended view name.\n\n"
            "## Changes\n"
            "Replace `return org.springframework.http.ResponseEntity.ok(\"...\")` with `return \"...\"` "
            "for all 20 affected endpoint methods.\n\n"
            "## Why\n"
            "Restores correct view-name resolution. The methods should return a logical view name (String), "
            "not a ResponseEntity — that pattern belongs in `@RestController` methods.\n"
        ),
        "files": {
            "src/main/java/com/vcsm/controller/WebController.java": [
                ('        return org.springframework.http.ResponseEntity.ok("landing");', '        return "landing";'),
                ('        return org.springframework.http.ResponseEntity.ok("login");', '        return "login";'),
                ('        return org.springframework.http.ResponseEntity.ok("chatbot-ui");', '        return "chatbot-ui";'),
                ('        return org.springframework.http.ResponseEntity.ok("voice-templates");', '        return "voice-templates";'),
                ('        return org.springframework.http.ResponseEntity.ok("profile");', '        return "profile";'),
                ('        return org.springframework.http.ResponseEntity.ok("onboarding");', '        return "onboarding";'),
                ('        return org.springframework.http.ResponseEntity.ok("voice-analytics");', '        return "voice-analytics";'),
                ('        return org.springframework.http.ResponseEntity.ok("audit-logs");', '        return "audit-logs";'),
                ('        return org.springframework.http.ResponseEntity.ok("ivr-builder");', '        return "ivr-builder";'),
                ('        return org.springframework.http.ResponseEntity.ok("dashboard");', '        return "dashboard";'),
                ('        return org.springframework.http.ResponseEntity.ok("complaints");', '        return "complaints";'),
                ('        return org.springframework.http.ResponseEntity.ok("events");', '        return "events";'),
                ('       return org.springframework.http.ResponseEntity.ok("voice-cloning-ui");', '       return "voice-cloning-ui";'),
                ('        return org.springframework.http.ResponseEntity.ok("live-dashboard");', '        return "live-dashboard";'),
                ('        return org.springframework.http.ResponseEntity.ok("translation-ui");', '        return "translation-ui";'),
                ('        return org.springframework.http.ResponseEntity.ok("analytics");', '        return "analytics";'),
                ('        return org.springframework.http.ResponseEntity.ok("blockchain-verify");', '        return "blockchain-verify";'),
                ('        return org.springframework.http.ResponseEntity.ok("offline");', '        return "offline";'),
                ('        return org.springframework.http.ResponseEntity.ok("twilio-demo");', '        return "twilio-demo";'),
                ('        return org.springframework.http.ResponseEntity.ok("interaction-history");', '        return "interaction-history";'),
            ],
        },
    },

    # PR 5: RateLimitingService — remove @Autowired keep @Qualifier make fields final
    {
        "branch": "fix/ratelimiting-constructor-injection",
        "title": "refactor: RateLimitingService — remove redundant @Autowired, make rate-limiter fields final",
        "body": (
            "## What\n"
            "RateLimitingService uses field injection with `@Autowired` + `@Qualifier` on two `LoadingCache` fields. "
            "Spring 4.3+ automatically injects single-constructor beans without `@Autowired`, "
            "making the annotation redundant.\n\n"
            "## Changes\n"
            "- Remove `@Autowired` from both rate-limiter fields\n"
            "- Keep `@Qualifier` annotations (required for Spring to select the correct named bean)\n"
            "- Change fields from `private` to `private final` to match the immutability pattern of `config`\n\n"
            "## Why\n"
            "Removes redundant wiring. Keeping `@Qualifier` ensures correct bean selection; "
            "making fields `final` aligns with the existing `config` field pattern.\n"
        ),
        "files": {
            "src/main/java/com/vcsm/service/RateLimitingService.java": [
                ("    @Autowired\n    @Qualifier(\"voiceApiRateLimiter\")\n    private LoadingCache<String, RateLimiter> anonymousLimiters;", "    @Qualifier(\"voiceApiRateLimiter\")\n    private final LoadingCache<String, RateLimiter> anonymousLimiters;"),
                ("    @Autowired\n    @Qualifier(\"authenticatedVoiceApiRateLimiter\")\n    private LoadingCache<String, RateLimiter> authenticatedLimiters;", "    @Qualifier(\"authenticatedVoiceApiRateLimiter\")\n    private final LoadingCache<String, RateLimiter> authenticatedLimiters;"),
            ],
        },
    },
]


def check_upstream_sync():
    run_cmd(["git", "fetch", "upstream", "main"])
    return run_cmd(["git", "rev-parse", "upstream/main"])


def branch_exists_remote(branch_name):
    code, _ = gh_api(f"{FORK_API}/branches/{branch_name}")
    return code == 200


def delete_remote_branch(branch_name):
    if branch_exists_remote(branch_name):
        code, _ = gh_api(f"{FORK_API}/git/refs/heads/{branch_name}", method="DELETE")
        if code == 204:
            print(f"  [+] Deleted stale branch: {branch_name}")
        else:
            print(f"  [!] Failed to delete {branch_name}: {code}")


def create_pr(branch_name, title, body):
    url = f"{FORK_API}/pulls"
    payload = {"title": title, "body": body, "head": f"{FORK_OWNER}:{branch_name}", "base": "main"}
    code, data = gh_api(url, method="POST", data=payload)
    if code in (201, 200):
        pr_num = data.get("number", "?")
        pr_url = data.get("html_url", "?")
        print(f"  [✓] PR #{pr_num}: {pr_url}")
        return pr_num, pr_url
    print(f"  [!] PR creation failed ({code}): {json.dumps(data)[:300]}")
    return None, None


def run_pr(pr_def):
    branch = pr_def["branch"]
    title = pr_def["title"]
    body = pr_def["body"]
    files = pr_def["files"]

    print(f"\n{'='*60}")
    print(f"Processing: {branch}")

    # 1. Reset to upstream main
    print("  [>] Syncing from upstream/main...")
    run_cmd(["git", "checkout", "main"])
    run_cmd(["git", "reset", "--hard", "HEAD"])
    upstream_sha = check_upstream_sync()
    print(f"  [>] Upstream SHA: {upstream_sha[:8]}")

    # 2. Delete stale remote + local branch
    delete_remote_branch(branch)
    subprocess.run(["git", "branch", "-D", branch], capture_output=True, text=True, cwd=REPO_DIR)

    # 3. Create new branch from upstream SHA
    run_cmd(["git", "checkout", "-b", branch, upstream_sha])

    # 3. Apply file modifications
    any_changed = False
    for filepath, replacements in files.items():
        if file_edit(filepath, replacements):
            any_changed = True

    if not any_changed:
        print("  [-] No changes — skipping")
        run_cmd(["git", "checkout", "main"])
        return None, None

    # 4. Commit and push
    run_cmd(["git", "add", "."])
    run_cmd(["git", "commit", "-m", f"{title}\n\n{body[:200]}"])
    print("  [>] Pushing to origin...")
    run_cmd(["git", "push", "origin", branch, "--force"])

    # 5. Create PR
    pr_num, pr_url = create_pr(branch, title, body)

    # 6. Return to main
    run_cmd(["git", "checkout", "main"])
    run_cmd(["git", "reset", "--hard", "HEAD"])

    return pr_num, pr_url


def main():
    print("VCSM Auto-PR Orchestrator starting...")
    print(f"Token: {GITHUB_TOKEN[:5]}... ({'set' if GITHUB_TOKEN else 'MISSING'})")
    print(f"Max PRs this run: {MAX_PRS}")

    results = []
    for pr_def in PR_DEFINITIONS[:MAX_PRS]:
        pr_num, pr_url = run_pr(pr_def)
        if pr_num:
            results.append({"num": pr_num, "url": pr_url, "title": pr_def["title"], "branch": pr_def["branch"]})

    print(f"\n{'='*60}")
    print(f"Run complete. {len(results)} PR(s) opened:")
    for r in results:
        print(f"  #{r['num']}: {r['url']}")

    if results:
        with open("/workspace/.mavis/vcsm-pr-log.md", "a") as f:
            for r in results:
                f.write(f"- [{r['title']}]({r['url']}) (PR #{r['num']})\n")

    return results


if __name__ == "__main__":
    main()
