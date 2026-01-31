# PyPI Publication Checklist

Use this checklist to track your progress through the publication process.

## Pre-Publication

- [ ] Update `YOUR-USERNAME` in pyproject.toml with actual GitHub username
  - [ ] Line 27: Homepage URL
  - [ ] Line 28: Repository URL
  - [ ] Line 29: Issues URL
- [ ] Review LICENSE file (already created)
- [ ] Review CHANGELOG.md (already created)
- [ ] Verify package builds: `uv build`
- [ ] Commit all changes
  ```bash
  git add .
  git commit -m "Prepare package for PyPI publication"
  git push
  ```

## PyPI Account Setup

- [ ] Create PyPI account at https://pypi.org/account/register/
- [ ] Verify email address
- [ ] Enable two-factor authentication (recommended)

## Choose Publishing Method

### Option A: Automated (Recommended)

- [ ] Configure Trusted Publishing on PyPI:
  - [ ] Go to https://pypi.org/manage/account/publishing/
  - [ ] Add pending publisher:
    - PyPI Project Name: `azure-updates-mcp`
    - Owner: [your GitHub username]
    - Repository: `azure-updates-mcp`
    - Workflow: `publish.yml`
    - Environment: `pypi`
- [ ] Create environment on GitHub:
  - [ ] Go to repository Settings → Environments
  - [ ] Create environment: `pypi`
- [ ] Create and push git tag:
  ```bash
  git tag v0.1.0
  git push origin v0.1.0
  ```
- [ ] Create GitHub release:
  - [ ] Go to repository → Releases → New release
  - [ ] Select tag: v0.1.0
  - [ ] Title: "v0.1.0 - Initial Release"
  - [ ] Description: Copy from CHANGELOG.md
  - [ ] Publish release
- [ ] Wait for GitHub Actions to complete
- [ ] Verify workflow succeeded in Actions tab

### Option B: Manual (Alternative)

- [ ] Create PyPI API token at https://pypi.org/manage/account/token/
- [ ] Install twine: `uv tool install twine`
- [ ] (Optional) Test with TestPyPI first:
  ```bash
  uvx twine upload --repository testpypi dist/*
  ```
- [ ] Upload to PyPI:
  ```bash
  uvx twine upload dist/*
  ```

## Post-Publication Verification

- [ ] Check package on PyPI: https://pypi.org/project/azure-updates-mcp/
- [ ] Verify metadata displays correctly
- [ ] Test installation from PyPI:
  ```bash
  uvx azure-updates-mcp@latest
  ```
- [ ] Test package works:
  ```bash
  uvx azure-updates-mcp
  # Should start the MCP server
  ```

## Update Documentation

- [ ] Replace README.md with README.post-publish.md:
  ```bash
  cp README.post-publish.md README.md
  ```
- [ ] Commit and push:
  ```bash
  git add README.md
  git commit -m "Update README for PyPI-published package"
  git push
  ```

## Test Installation Methods

- [ ] VS Code one-click install:
  - [ ] Click VS Code badge in README
  - [ ] Verify installation succeeds
  - [ ] Verify server appears in VS Code MCP settings
- [ ] Cursor one-click install:
  - [ ] Click Cursor badge in README
  - [ ] Verify installation succeeds
- [ ] Claude Desktop:
  - [ ] Add to claude_desktop_config.json with `uvx azure-updates-mcp`
  - [ ] Restart Claude Desktop
  - [ ] Verify server connects
- [ ] Claude Code:
  - [ ] Run: `claude mcp add --transport stdio azure-updates -- uvx azure-updates-mcp`
  - [ ] Verify: `claude mcp list`
  - [ ] Test server works
- [ ] Copilot CLI:
  - [ ] Add to mcp-config.json with `uvx azure-updates-mcp`
  - [ ] Test server works

## Optional Enhancements

- [ ] Set up pre-commit hooks:
  ```bash
  pip install pre-commit
  pre-commit install
  ```
- [ ] Register in MCP Registry:
  - [ ] Visit https://registry.modelcontextprotocol.io/
  - [ ] Follow submission process
- [ ] Add package to awesome-mcp lists
- [ ] Create documentation website (optional)
- [ ] Add badges to README:
  - [ ] PyPI version
  - [ ] Python versions
  - [ ] License
  - [ ] Downloads

## Troubleshooting Reference

If you encounter issues, refer to:
- PUBLISHING.md - Detailed instructions and troubleshooting
- https://packaging.python.org/tutorials/packaging-projects/
- https://docs.pypi.org/trusted-publishers/

## Success Criteria

✅ Package published to PyPI
✅ One-click install badges work
✅ Users can install with `uvx azure-updates-mcp`
✅ All MCP clients can connect successfully
✅ README reflects PyPI installation

---

**Current Status:** Pre-Publication
**Next Action:** Update pyproject.toml URLs and commit changes
