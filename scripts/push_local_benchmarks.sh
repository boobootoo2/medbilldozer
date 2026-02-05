#!/bin/bash
# Push local benchmark results to Supabase
# Usage: ./scripts/push_local_benchmarks.sh [model1] [model2] ...
# Example: ./scripts/push_local_benchmarks.sh baseline gemini medgemma

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}Push Local Benchmark Results to Supabase${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Check if .env exists and has Supabase credentials
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create a .env file with SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"
    exit 1
fi

if ! grep -q "SUPABASE_URL" .env || ! grep -q "SUPABASE_SERVICE_ROLE_KEY" .env; then
    echo -e "${RED}❌ Error: Supabase credentials not found in .env${NC}"
    echo "Please add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to your .env file"
    exit 1
fi

# Get git metadata
COMMIT_SHA=$(git rev-parse HEAD)
BRANCH_NAME=$(git branch --show-current)
TRIGGERED_BY=$(whoami)

echo -e "📋 ${BLUE}Metadata:${NC}"
echo -e "   Commit: ${COMMIT_SHA:0:8}"
echo -e "   Branch: $BRANCH_NAME"
echo -e "   User: $TRIGGERED_BY"
echo ""

# Create temp directory for monitoring format files
TEMP_DIR="./temp-benchmark-artifacts"
mkdir -p "$TEMP_DIR"

# Determine which models to process
if [ $# -eq 0 ]; then
    # No arguments - process all available patient benchmark files
    MODELS=()
    for file in benchmarks/results/patient_benchmark_*.json; do
        if [ -f "$file" ]; then
            model=$(basename "$file" | sed 's/patient_benchmark_//' | sed 's/.json//')
            MODELS+=("$model")
        fi
    done
    
    if [ ${#MODELS[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No patient benchmark results found${NC}"
        echo "Run benchmarks first: python3 scripts/generate_patient_benchmarks.py"
        exit 1
    fi
    
    echo -e "${GREEN}Found ${#MODELS[@]} model result(s): ${MODELS[*]}${NC}"
    echo ""
else
    # Use provided models
    MODELS=("$@")
fi

# Convert and push each model's results
SUCCESS_COUNT=0
FAIL_COUNT=0

for model in "${MODELS[@]}"; do
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Processing: $model${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    INPUT_FILE="benchmarks/results/patient_benchmark_${model}.json"
    MONITORING_FILE="$TEMP_DIR/${model}_benchmark_results.json"
    
    # Check if input file exists
    if [ ! -f "$INPUT_FILE" ]; then
        echo -e "${YELLOW}⚠️  Skipping $model: No results file found ($INPUT_FILE)${NC}"
        echo ""
        continue
    fi
    
    # Step 1: Convert to monitoring format
    echo -e "📊 Converting to monitoring format..."
    if python3 scripts/convert_benchmark_to_monitoring.py \
        --input "$INPUT_FILE" \
        --output "$MONITORING_FILE" \
        --model "$model"; then
        echo -e "${GREEN}✅ Conversion successful${NC}"
    else
        echo -e "${RED}❌ Conversion failed${NC}"
        ((FAIL_COUNT++))
        echo ""
        continue
    fi
    
    # Step 2: Push to Supabase
    echo -e "☁️  Pushing to Supabase..."
    if python3 scripts/push_to_supabase.py \
        --input "$MONITORING_FILE" \
        --environment local \
        --commit-sha "$COMMIT_SHA" \
        --branch-name "$BRANCH_NAME" \
        --triggered-by "$TRIGGERED_BY" \
        --notes "Manual push from local benchmark run (V2 structured reasoning prompt)" \
        --tags "v2-structured-reasoning" "local-run" "prompt-enhancement"; then
        echo -e "${GREEN}✅ Successfully pushed $model results${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}❌ Failed to push $model results${NC}"
        ((FAIL_COUNT++))
    fi
    
    echo ""
done

# Cleanup
rm -rf "$TEMP_DIR"

# Summary
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}✅ Successful: $SUCCESS_COUNT${NC}"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAIL_COUNT${NC}"
fi
echo ""

if [ $SUCCESS_COUNT -gt 0 ]; then
    echo -e "${GREEN}🎉 Benchmark results have been pushed to Supabase!${NC}"
    echo -e "View results at your Streamlit dashboard"
else
    echo -e "${RED}❌ No results were successfully pushed${NC}"
    exit 1
fi
