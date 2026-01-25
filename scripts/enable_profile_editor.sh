#!/bin/bash
# Enable Profile Editor Feature
# This script helps you quickly enable the Profile Editor in medBillDozer

set -e

echo "🚜 medBillDozer - Profile Editor Setup"
echo "======================================"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "✓ Found existing .env file"
    echo ""
    
    # Check if PROFILE_EDITOR_ENABLED already exists
    if grep -q "PROFILE_EDITOR_ENABLED" .env; then
        echo "⚠️  PROFILE_EDITOR_ENABLED already exists in .env"
        echo "Current value:"
        grep "PROFILE_EDITOR_ENABLED" .env
        echo ""
        read -p "Update it to TRUE? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Update existing value
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' 's/^PROFILE_EDITOR_ENABLED=.*/PROFILE_EDITOR_ENABLED=TRUE/' .env
            else
                # Linux
                sed -i 's/^PROFILE_EDITOR_ENABLED=.*/PROFILE_EDITOR_ENABLED=TRUE/' .env
            fi
            echo "✓ Updated PROFILE_EDITOR_ENABLED=TRUE"
        fi
    else
        # Add new entry
        echo "" >> .env
        echo "# Profile Editor Feature" >> .env
        echo "PROFILE_EDITOR_ENABLED=TRUE" >> .env
        echo "✓ Added PROFILE_EDITOR_ENABLED=TRUE to .env"
    fi
    
    # Check if IMPORTER_ENABLED already exists
    if grep -q "IMPORTER_ENABLED" .env; then
        echo ""
        echo "⚠️  IMPORTER_ENABLED already exists in .env"
        echo "Current value:"
        grep "IMPORTER_ENABLED" .env
        echo ""
        read -p "Update it to TRUE? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Update existing value
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' 's/^IMPORTER_ENABLED=.*/IMPORTER_ENABLED=TRUE/' .env
            else
                # Linux
                sed -i 's/^IMPORTER_ENABLED=.*/IMPORTER_ENABLED=TRUE/' .env
            fi
            echo "✓ Updated IMPORTER_ENABLED=TRUE"
        fi
    else
        # Add new entry
        echo "IMPORTER_ENABLED=TRUE" >> .env
        echo "✓ Added IMPORTER_ENABLED=TRUE to .env"
    fi
else
    echo "⚠️  No .env file found"
    echo ""
    read -p "Create .env from .env.example? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            echo "✓ Created .env from .env.example"
            
            # Update the values
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' 's/^PROFILE_EDITOR_ENABLED=.*/PROFILE_EDITOR_ENABLED=TRUE/' .env
                sed -i '' 's/^IMPORTER_ENABLED=.*/IMPORTER_ENABLED=TRUE/' .env
            else
                # Linux
                sed -i 's/^PROFILE_EDITOR_ENABLED=.*/PROFILE_EDITOR_ENABLED=TRUE/' .env
                sed -i 's/^IMPORTER_ENABLED=.*/IMPORTER_ENABLED=TRUE/' .env
            fi
            echo "✓ Enabled PROFILE_EDITOR_ENABLED=TRUE"
            echo "✓ Enabled IMPORTER_ENABLED=TRUE"
        else
            echo "❌ .env.example not found"
            echo "Creating minimal .env with Profile Editor enabled..."
            cat > .env << EOF
# medBillDozer Environment Variables

# Profile Editor Feature
PROFILE_EDITOR_ENABLED=TRUE
IMPORTER_ENABLED=TRUE

# Add your API keys below
OPENAI_API_KEY=
GOOGLE_API_KEY=
EOF
            echo "✓ Created .env with Profile Editor enabled"
        fi
    else
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    mkdir -p data
    echo "✓ Created data/ directory for profile storage"
else
    echo "✓ data/ directory already exists"
fi

# Add to .gitignore if not already there
if [ -f .gitignore ]; then
    if ! grep -q "^data/.*\.json$" .gitignore; then
        echo "" >> .gitignore
        echo "# Profile Editor data files (privacy)" >> .gitignore
        echo "data/*.json" >> .gitignore
        echo "✓ Added data/*.json to .gitignore"
    else
        echo "✓ data/*.json already in .gitignore"
    fi
fi

echo ""
echo "======================================"
echo "✅ Profile Editor Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Run: streamlit run app.py"
echo "2. Look for the 📋 Profile button in the sidebar"
echo "3. Start adding your information!"
echo ""
echo "📚 For more help, see:"
echo "   - PROFILE_EDITOR_QUICKSTART.md"
echo "   - PROFILE_EDITOR_INTEGRATION.md"
echo ""
