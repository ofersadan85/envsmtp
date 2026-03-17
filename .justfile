set windows-shell := ["pwsh", "-Command"]
set shell := ["bash", "-c"]

default: check test

check:
    uv tool run ruff check
    uv tool run ty check

test *tests:
    uv run pytest --cov=envsmtp --cov-report=term-missing --cov-report=xml:coverage.xml --cov-report=html:htmlcov {{tests}}
