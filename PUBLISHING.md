# Publishing azure-updates-mcp to PyPI

This guide walks you through publishing the package to PyPI, which will enable one-click install badges to work.

## Prerequisites

- [x] Package builds successfully (`uv build` completed)
- [x] README.md is complete and well-formatted
- [x] LICENSE file exists
- [x] CHANGELOG.md created
- [x] GitHub Actions workflow created

## Step 1: Create PyPI Account (if needed)

1. Go to https://pypi.org/account/register/
2. Create an account and verify your email
3. Enable two-factor authentication (recommended)

## Step 2: Configure Trusted Publishing (Recommended)

Trusted Publishing eliminates the need for API tokens and is more secure.

### On PyPI:

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the form:
   - **PyPI Project Name**: `azure-updates-mcp`
   - **Owner**: Your GitHub username or organization
   - **Repository name**: `azure-updates-mcp`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click "Add"

### On GitHub:

1. Go to your repository settings
2. Navigate to Environments → New environment
3. Create environment named `pypi`
4. (Optional) Add deployment protection rules

## Step 3: Publish the Package

### Option A: Using GitHub Release (Automated - Recommended)

1. Create a new release on GitHub:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
2. Go to your repository on GitHub
3. Click "Releases" → "Create a new release"
4. Select the tag `v0.1.0`
5. Title: "v0.1.0 - Initial Release"
6. Description: Copy from CHANGELOG.md
7. Click "Publish release"
8. GitHub Actions will automatically build and publish to PyPI

### Option B: Manual Publish (For Testing)

If you need to publish manually first:

1. Install publishing tools:
   ```bash
   uv tool install twine
   ```

2. Create API token on PyPI:
   - Go to https://pypi.org/manage/account/token/
   - Create token with scope "Entire account" or specific to project
   - Save the token (starts with `pypi-`)

3. Publish to TestPyPI first (recommended):
   ```bash
   uv build
   uvx twine upload --repository testpypi dist/*
   ```
   - Username: `__token__`
   - Password: Your TestPyPI token

4. Test installation from TestPyPI:
   ```bash
   uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple azure-updates-mcp
   ```

5. If successful, publish to PyPI:
   ```bash
   uvx twine upload dist/*
   ```
   - Username: `__token__`
   - Password: Your PyPI token

## Step 4: Verify Publication

1. Check package page: https://pypi.org/project/azure-updates-mcp/
2. Verify metadata displays correctly
3. Test installation:
   ```bash
   uvx azure-updates-mcp@latest
   ```

## Step 5: Test One-Click Install Badges

1. Click the VS Code badge in README.md:7
2. Verify VS Code installs the package from PyPI
3. Test the Cursor badge similarly

## Step 6: Update README.md (After Publishing)

Once published, update the installation instructions to use the simpler PyPI-based commands:

### Before (local installation):
```json
{
  "command": "uv",
  "args": ["run", "--directory", "/path/to/azure-updates-mcp", "azure-updates-mcp"]
}
```

### After (PyPI installation):
```json
{
  "command": "uvx",
  "args": ["azure-updates-mcp"]
}
```

## Troubleshooting

### Package name already taken
If `azure-updates-mcp` is taken, choose an alternative:
- `azure-updates-mcp-server`
- `mcp-azure-updates`
- Check availability: https://pypi.org/project/YOUR-NAME/

### Build fails
```bash
# Clean build artifacts
rm -rf dist/
uv build
```

### Trusted Publishing not working
1. Verify environment name matches exactly: `pypi`
2. Check workflow file name matches: `publish.yml`
3. Ensure permissions include `id-token: write`
4. Wait 5-10 minutes after configuring PyPI

### Upload fails with 403 error
- Check API token is correct and not expired
- Verify token has correct scope
- For Trusted Publishing, ensure GitHub Actions has proper permissions

## Future Releases

For subsequent releases:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Commit changes
4. Create and push tag:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
5. Create GitHub release
6. GitHub Actions will automatically publish

## Resources

- [PyPI Documentation](https://packaging.python.org/tutorials/packaging-projects/)
- [Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [uv Documentation](https://docs.astral.sh/uv/)
