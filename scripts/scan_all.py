import os
import sys
import subprocess
import json
from pathlib import Path

REPOS = {
    "global-tracker-spark": "/home/demo/global-tracker-spark",
    "blue-green-gateway": "/home/demo/blue-green-gateway",
    "pipelineguard": "/home/demo/pipelineguard",
    "clue-bdi-portfolio": "/home/demo/clue-bdi-portfolio",
    "cluebdi-vitality-compass": "/home/demo/cluebdi-vitality-compass"
}

def run_cmd(args, cwd=None, env=None):
    print(f"Running: {' '.join(args)} in {cwd or '.'}")
    res = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running {' '.join(args)}:")
        print(res.stderr)
    return res

def main():
    pg_dir = Path("/home/demo/pipelineguard")
    vr_dir = Path("/home/demo/VR")
    vr_dir.mkdir(parents=True, exist_ok=True)
    
    # We will accumulate all findings
    report_data = {}
    
    for repo_name, repo_path in REPOS.items():
        print(f"\n==========================================")
        print(f"Scanning {repo_name}...")
        print(f"==========================================")
        
        env = os.environ.copy()
        env["TARGET_REPO_NAME"] = repo_name
        env["TARGET_REPO_PATH"] = repo_path
        env["FAIL_ON_SECRET"] = "false"
        
        # Run Phase 1
        run_cmd(["bash", "./scripts/run_phase1.sh"], cwd=pg_dir, env=env)
        # Run Phase 2
        run_cmd(["bash", "./scripts/run_phase2.sh"], cwd=pg_dir, env=env)
        # Run Correlation
        run_cmd(["uv", "run", "python", "-m", "scripts.correlate_findings"], cwd=pg_dir, env=env)
        
        findings_file = pg_dir / "normalized" / repo_name / "findings.jsonl"
        findings = []
        if findings_file.exists():
            with open(findings_file, "r") as f:
                for line in f:
                    if line.strip():
                        findings.append(json.loads(line))
        
        incidents_file = pg_dir / "correlated" / repo_name / "incidents.jsonl"
        incidents = []
        if incidents_file.exists():
            with open(incidents_file, "r") as f:
                for line in f:
                    if line.strip():
                        incidents.append(json.loads(line))
                        
        report_data[repo_name] = {
            "findings": findings,
            "incidents": incidents
        }
        
    # Generate Report
    report_lines = []
    report_lines.append("# Vulnerability Report - CLUE-BDI Portfolio")
    report_lines.append(f"Generated at: {subprocess.check_output(['date']).decode().strip()}\n")
    
    for repo_name, data in report_data.items():
        findings = data["findings"]
        incidents = data["incidents"]
        
        # Filter for critical / high
        vulns = [f for f in findings if f.get("severity") in ("critical", "high")]
        
        report_lines.append(f"## Repository: `{repo_name}`")
        report_lines.append(f"- **Total Findings**: {len(findings)}")
        report_lines.append(f"- **Critical/High Severity Findings**: {len(vulns)}")
        report_lines.append(f"- **Correlated Incidents**: {len(incidents)}\n")
        
        if vulns:
            report_lines.append("| Severity | Tool | Category | Title | File Path | Line | Description |")
            report_lines.append("| --- | --- | --- | --- | --- | --- | --- |")
            for v in vulns:
                severity = v.get("severity", "unknown").upper()
                tool = v.get("tool", "unknown")
                category = v.get("category", "unknown")
                title = v.get("title", "unknown")
                file_path = v.get("file_path", "unknown")
                line = v.get("line_start", "0")
                desc = v.get("description", "unknown").replace("\n", " ")[:150]
                report_lines.append(f"| **{severity}** | {tool} | {category} | {title} | `{file_path}` | {line} | {desc} |")
        else:
            report_lines.append("*No Critical or High issues found.*\n")
            
        report_lines.append("")
        
    report_path = vr_dir / "Vulnerability_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
        
    print(f"\nReport written successfully to: {report_path}")

if __name__ == "__main__":
    main()
