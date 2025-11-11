# VS Code Extension Publishing Workflow

This GitHub Action workflow automatically publishes the SynapseLang VS Code extension to both:
- **Open VSX Registry** (used by VSCodium, Gitpod, Eclipse Theia, etc.)
- **Visual Studio Marketplace** (official VS Code marketplace)

## Setup Instructions

### 1. Generate Publishing Tokens

#### Open VSX Registry Token
1. Visit https://open-vsx.org/
2. Sign in with your GitHub account
3. Go to your user settings → Access Tokens
4. Create a new access token with publishing permissions
5. Copy the token

#### Visual Studio Marketplace Token
1. Visit https://dev.azure.com/
2. Sign in with your Microsoft account
3. Go to User Settings → Personal Access Tokens
4. Create a new token with:
   - Organization: All accessible organizations
   - Scopes: Marketplace (Manage)
5. Copy the token

### 2. Add Secrets to GitHub Repository

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add two new repository secrets:
   - `OPEN_VSX_TOKEN`: Paste your Open VSX token
   - `VS_MARKETPLACE_TOKEN`: Paste your Visual Studio Marketplace token

### 3. Trigger the Workflow

The workflow can be triggered in two ways:

#### Automatic (Recommended)
Push a version tag to trigger automatic publishing:
```bash
git tag v0.2.0
git push origin v0.2.0
```

#### Manual
1. Go to Actions tab in your repository
2. Select "Publish VS Code Extension" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

## Workflow Features

- ✅ Publishes to both Open VSX Registry and Visual Studio Marketplace
- ✅ Skips duplicate versions automatically
- ✅ Continues on error (won't fail if one registry fails)
- ✅ Uses Node.js 20 for latest compatibility
- ✅ Caches npm dependencies for faster builds
- ✅ Builds extension before publishing

## Version Management

The extension version is defined in `vscode-extension/package.json`. When creating a new release:

1. Update the version in `package.json`
2. Commit the changes
3. Create and push a git tag matching the version (e.g., `v0.2.0`)
4. The workflow will automatically publish the new version

## Troubleshooting

### Publishing Fails
- Verify your tokens are valid and have the correct permissions
- Check that the version in `package.json` hasn't been published already
- Review the workflow logs in the Actions tab

### Version Already Exists
The workflow includes `skipDuplicate: true`, so it will gracefully skip versions that already exist.

## Manual Publishing

If you prefer to publish manually, you can still use:
```bash
cd vscode-extension
npm run package  # Creates .vsix file
npx vsce publish  # Publishes to VS Marketplace
npx ovsx publish  # Publishes to Open VSX
```

## Links

- [HaaLeo/publish-vscode-extension](https://github.com/HaaLeo/publish-vscode-extension) - The GitHub Action used
- [Open VSX Registry](https://open-vsx.org/)
- [Visual Studio Marketplace](https://marketplace.visualstudio.com/)
