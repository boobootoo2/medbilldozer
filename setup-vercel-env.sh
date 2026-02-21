#!/usr/bin/env zsh

# Script to add all Firebase environment variables to Vercel
# Run this script from the project root directory

echo "🔧 Adding Firebase environment variables to Vercel..."
echo ""

# Function to add environment variable to all environments
add_env_var() {
    local key=$1
    local value=$2

    echo "📝 Adding $key..."

    # Add to production
    if echo "$value" | vercel env add "$key" production --yes >/dev/null 2>&1; then
        echo "  ✅ Added to production"
    else
        echo "  ℹ️  Already exists in production"
    fi

    # Add to preview
    if echo "$value" | vercel env add "$key" preview --yes >/dev/null 2>&1; then
        echo "  ✅ Added to preview"
    else
        echo "  ℹ️  Already exists in preview"
    fi

    # Add to development
    if echo "$value" | vercel env add "$key" development --yes >/dev/null 2>&1; then
        echo "  ✅ Added to development"
    else
        echo "  ℹ️  Already exists in development"
    fi

    echo ""
}

# Add each environment variable
add_env_var "VITE_FIREBASE_API_KEY" "AIzaSyAubD9WLDgqMkAq1NXEsBzWK1KVV6PAFJQ"
add_env_var "VITE_FIREBASE_AUTH_DOMAIN" "medbilldozer.firebaseapp.com"
add_env_var "VITE_FIREBASE_PROJECT_ID" "medbilldozer"
add_env_var "VITE_FIREBASE_STORAGE_BUCKET" "medbilldozer.firebasestorage.app"
add_env_var "VITE_FIREBASE_MESSAGING_SENDER_ID" "360553024921"
add_env_var "VITE_FIREBASE_APP_ID" "1:360553024921:web:5abbc9b9f2109f87a31708"
add_env_var "VITE_FIREBASE_MEASUREMENT_ID" "G-BVDCZMG006"
add_env_var "VITE_INVITE_CODES" "MEDBILL2024,ALPHA,BETA,2026MEDGEMMA"

echo "🎉 All environment variables have been configured!"
echo ""
echo "📋 Next steps:"
echo "1. Redeploy your app to pick up the new environment variables"
echo "2. Add your Vercel domain to Firebase authorized domains"
