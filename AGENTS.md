For backend development, use `uv` for dependency management.

Useful Commands

    # Sync dependencies from lockfile
    uv sync

    # Add a new package
    uv add <PACKAGE-NAME>

    # Run Python files
    uv run python <PYTHON-FILE>


ensure each CLUEBDI repository has this AGENTS.md file.

regularly commit code to git and push.

regularly ensure all CLUEBDI repositories (global-tracker-spark, blue-green-gateway, pipelineguard, clue-bdi-portfolio, cluebdi-vitality-compass) have similar directory structure with docs folder for mkdocs with deploy_guide.md, dev guides with intial to final setup instructions, and other relevant sections as appropriate for project and a README.md.

regularly run all CLUEBDI repositories (global-tracker-spark, blue-green-gateway, pipelineguard, clue-bdi-portfolio, cluebdi-vitality-compass) through pipeline guard and try to resolve any critical or hight issues. Save the report to a Vulnerability_report.md file in the VR folder outside in the home directory /home/demo.