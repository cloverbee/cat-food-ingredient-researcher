#!/bin/bash
# Setup pre-commit hooks for development

set -e

echo "🔧 Setting up pre-commit hooks..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo -e "${BLUE}Installing pre-commit...${NC}"
    pip install pre-commit
fi

# Install the hooks
echo -e "${BLUE}Installing git hooks...${NC}"
pre-commit install

echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
echo ""

# Ask if user wants to run on all files
read -p "Do you want to run pre-commit on all existing files? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Running pre-commit on all files...${NC}"
    echo "This may take a moment and will format all Python files."
    echo ""

    if pre-commit run --all-files; then
        echo ""
        echo -e "${GREEN}✓ All checks passed!${NC}"
    else
        echo ""
        echo -e "${RED}Some files were modified or have issues.${NC}"
        echo "Please review the changes and commit them:"
        echo "  git add ."
        echo "  git commit -m 'chore: apply code formatting'"
    fi
else
    echo "Skipping full repository check."
    echo "Pre-commit will run automatically on your next commit."
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Pre-commit will now run automatically before each commit."
echo ""
echo "Useful commands:"
echo "  pre-commit run --all-files    # Run on all files"
echo "  pre-commit run                # Run on staged files"
echo "  SKIP=flake8 git commit        # Skip specific hook"
echo "  git commit --no-verify        # Skip all hooks (not recommended)"
echo ""
