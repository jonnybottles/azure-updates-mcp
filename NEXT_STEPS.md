# Next Steps for Publishing azure-updates-mcp to PyPI

## What's Been Prepared

The following files have been created/updated to prepare your package for PyPI publication:

### ✅ Core Package Files
- **LICENSE** - MIT license file (required by PyPI)
- **CHANGELOG.md** - Version history (recommended for PyPI)
- **pyproject.toml** - Enhanced with PyPI metadata (authors, keywords, classifiers, URLs)

### ✅ Automation & Documentation
- **.github/workflows/publish.yml** - GitHub Actions workflow for automated publishing
- **PUBLISHING.md** - Complete step-by-step guide for publishing to PyPI
- **README.post-publish.md** - Updated README to use after PyPI publication
- **NEXT_STEPS.md** - This file

### ✅ Package Build
- Package builds successfully: `dist/azure_updates_mcp-0.1.0.tar.gz` and `dist/azure_updates_mcp-0.1.0-py3-none-any.whl`

## What You Need to Do

### Step 1: Update GitHub Repository URLs

The pyproject.toml currently has placeholder URLs. Update them with your actual GitHub username/organization:

**In pyproject.toml lines 27-29:**
```toml
[project.urls]
Homepage = "https://github.com/YOUR-USERNAME/azure-updates-mcp"
Repository = "https://github.com/YOUR-USERNAME/azure-updates-mcp"
Issues = "https://github.com/YOUR-USERNAME/azure-updates-mcp/issues"
```

Replace `YOUR-USERNAME` with your actual GitHub username or organization.

### Step 2: Commit and Push Changes

```bash
git add .
git commit -m "Prepare package for PyPI publication

- Add LICENSE file
- Add CHANGELOG.md
- Enhance pyproject.toml with PyPI metadata
- Add GitHub Actions workflow for automated publishing
- Add publishing documentation
"
git push
```

### Step 3: Choose Publishing Method

You have two options:

#### Option A: Automated Publishing with Trusted Publishing (Recommended)

This is the modern, secure approach used by professional projects.

1. **Create PyPI account** if you don't have one: https://pypi.org/account/register/
2. **Configure Trusted Publishing** on PyPI:
   - Go to https://pypi.org/manage/account/publishing/
   - Click "Add a new pending publisher"
   - Fill in:
     - PyPI Project Name: `azure-updates-mcp`
     - Owner: Your GitHub username
     - Repository name: `azure-updates-mcp`
     - Workflow name: `publish.yml`
     - Environment name: `pypi`
3. **Create environment on GitHub**:
   - Go to repository Settings → Environments
   - Create new environment: `pypi`
4. **Create a GitHub release**:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
   - Then go to GitHub → Releases → Create new release
   - Select tag v0.1.0
   - Title: "v0.1.0 - Initial Release"
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"
5. **GitHub Actions will automatically publish** to PyPI

See PUBLISHING.md for detailed instructions.

#### Option B: Manual Publishing

For quick testing or if you prefer manual control:

1. **Create PyPI account and API token**: https://pypi.org/manage/account/token/
2. **Publish**:
   ```bash
   # Install twine
   uv tool install twine

   # Upload to PyPI
   uvx twine upload dist/*
   ```
   - Username: `__token__`
   - Password: Your PyPI token

See PUBLISHING.md for detailed instructions including testing with TestPyPI first.

### Step 4: Verify Publication

1. Visit https://pypi.org/project/azure-updates-mcp/
2. Test installation:
   ```bash
   uvx azure-updates-mcp@latest
   ```
3. Click the VS Code badge in README.md to test one-click install

### Step 5: Update README After Publishing

Once the package is published to PyPI:

1. Replace README.md with README.post-publish.md:
   ```bash
   cp README.post-publish.md README.md
   git commit -m "Update README for PyPI-published package"
   git push
   ```

This updates all installation instructions to use the simpler `uvx azure-updates-mcp` command instead of requiring local installation.

### Step 6: Test All Installation Methods

After publishing, verify all installation methods work:

- ✅ **VS Code one-click install** - Click badge in README
- ✅ **Cursor one-click install** - Click badge in README
- ✅ **Claude Desktop** - Add to config with `uvx azure-updates-mcp`
- ✅ **Claude Code** - `claude mcp add --transport stdio azure-updates-mcp -- uvx azure-updates-mcp`
- ✅ **Copilot CLI** - Add to config with `uvx azure-updates-mcp`

## Benefits After Publishing

Once published to PyPI:

1. ✅ **One-click install badges work** - VS Code and Cursor can install automatically
2. ✅ **No local installation needed** - Users can run `uvx azure-updates-mcp` from anywhere
3. ✅ **Simpler config** - No need for `--directory` flags or file paths
4. ✅ **Discoverable** - Appears on PyPI for others to find
5. ✅ **Automated updates** - GitHub Actions publishes new versions automatically

## Optional: Register in MCP Registry

After publishing to PyPI, you can optionally register your server in the official MCP Registry for increased discoverability:

- Visit https://registry.modelcontextprotocol.io/
- Follow their submission process
- Your server will appear in the official MCP server directory

## Questions?

Refer to PUBLISHING.md for detailed instructions on each step, including troubleshooting.

## Summary

**Immediate actions:**
1. Update GitHub URLs in pyproject.toml (YOUR-USERNAME)
2. Commit and push changes
3. Follow PUBLISHING.md to publish to PyPI
4. Update README.md with README.post-publish.md
5. Test one-click install badges

**Result:**
✅ One-click install badges will work
✅ Users can install with `uvx azure-updates-mcp`
✅ Package follows industry best practices
✅ Automated publishing for future releases
