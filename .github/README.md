 [![Run Tests](https://github.com/boobootoo2/medbilldozer/actions/workflows/python-app.yml/badge.svg)](https://github.com/boobootoo2/medbilldozer/actions/workflows/python-app.yml)

![CodeQL](https://github.com/boobootoo2/medbilldozer/actions/workflows/codeql.yml/badge.svg)

![Security Audit](https://github.com/boobootoo2/medbilldozer/actions/workflows/security.yml/badge.svg)

[![Run Benchmarks](https://github.com/boobootoo2/medbilldozer/actions/workflows/run_benchmarks.yml/badge.svg)](https://github.com/boobootoo2/medbilldozer/actions/workflows/run_benchmarks.yml)

# medBillDozer

**medBillDozer** is an AI-powered assistant that helps patients audit medical bills
and explanations of benefits (EOBs) by detecting likely billing errors and
explaining them in plain language.

## Features


- **📖 [Quick Start Guide](https://github.com/boobootoo2/medbilldozer/blob/main/docs/QUICKSTART.md)** – Get up and running in 5 minutes
- **📚 [User Guide](https://github.com/boobootoo2/medbilldozer/blob/main/docs/USER_GUIDE.md)** – Comprehensive end-user documentation
- **⚙️ [Configuration Guide](https://github.com/boobootoo2/medbilldozer/blob/main/CONFIG_README.md)** – Feature flags and app configuration
- **🔧 [Technical Documentation](https://github.com/boobootoo2/medbilldozer/blob/main/docs/)** – API reference, modules, dependencies
- **🧠 [MedGemma & HAI-DEF Alignment](https://github.com/boobootoo2/medbilldozer/blob/main/docs/HAI_DEF_ALIGNMENT.md)** – How this project uses healthcare-aligned foundation models
- **📝 [Contributing](https://github.com/boobootoo2/medbilldozer/blob/main/DOCUMENTATION.md)** – How to contribute and maintain docs


## Why medBillDozer Is Different

Most consumer medical billing tools are manual, partial, or reactive.  
medBillDozer is built to systematically reconcile bills, claims, EOBs, and receipts — the point where most billing errors actually occur.

📄 **Learn more:**  
- [The Hidden Cost of Medical Billing Errors](https://github.com/boobootoo2/medbilldozer/blob/main/docs/the_hidden_cost)  
- [Competitive Landscape](https://github.com/boobootoo2/medbilldozer/blob/main/docs/competitive_landscape.md)




## Quick Start

### Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 5-Minute Tutorial

1. **Set up an API key** (optional - or use free "Local Heuristic" mode):
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # or use GOOGLE_API_KEY for Gemini
   ```

2. **Launch and try a demo**:
   - Accept privacy policy
   - Check "🏥 Colonoscopy Bill" in demo section
   - Click "Analyze with medBillDozer"
   - Review savings and issues found!

3. **Analyze your own bills**:
   - Copy text from any medical bill, EOB, or receipt
   - Paste into document input area
   - Click analyze and get instant feedback


## Demo

See the video demo submitted to the MedGemma Impact Challenge.

## What Documents Can I Analyze?

✅ Medical procedure bills (with CPT codes)  
✅ Dental treatment bills (with CDT codes)  
✅ Pharmacy receipts  
✅ Insurance Explanation of Benefits (EOB)  
✅ FSA/HSA claim statements  

## Privacy & Security

Your data never leaves your control:
- ✅ No data storage or databases
- ✅ Session-only processing
- ✅ No user accounts or tracking
- ✅ Clear on browser close

**Note**: Document text is sent to your chosen AI provider for analysis. Use "Local Heuristic" mode for 100% offline processing.

## Disclaimer

This project is a **prototype for educational purposes only**.

⚠️ medBillDozer does NOT provide:
- Medical, legal, or financial advice
- HIPAA-compliant healthcare services
- Guaranteed savings or outcomes
- Professional billing review

**Always verify findings** with your insurance company and consult qualified professionals for billing disputes.

## Cross-Document Analysis Results 🏥

_Patient-level domain knowledge detection across multiple documents._

### Model Comparison

| Model | Precision | Recall | F1 | Domain Knowledge Detection |
|-------|-----------|--------|----|-----------|
| Google MedGemma-4B-IT | 0.54 | 0.31 | 0.38 | 33.7% ✅ |
| OpenAI GPT-4 | 0.00 | 0.00 | 0.00 | 0.0%  |
| Google Gemini 1.5 Pro | 0.00 | 0.00 | 0.00 | 0.0%  |
| Heuristic Baseline | 0.00 | 0.00 | 0.00 | 0.0%  |

_Generated: 2026-02-05 14:56:47_

## Benchmark Analysis

_Evaluated on 6 synthetic healthcare billing documents._

### MedGemma Single-Document Results

- **Extraction Accuracy**: 100.0%
- **Issue Detection Precision**: 0.00
- **Issue Detection Recall**: 0.00
- **Issue Detection F1 Score**: 0.00
- **JSON Validity Rate**: 100.0%
- **Avg Extraction Time**: 0.00s
- **Avg Full Pipeline Time**: 2.19s

_Generated: 2026-02-03 11:12:17_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## 📊 Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents (medical bills, dental bills, EOBs, pharmacy receipts)._  
_Last updated: 2026-02-03 12:57:17_

### Model Performance Comparison

| Model | Success Rate | Precision | Recall | F1 Score | Avg Latency |
|-------|-------------|-----------|--------|----------|-------------|
| ✅ MedGemma (Hugging Face) | 100% (16/16) | 0.13 | 0.50 | 0.21 | 2.96s |
| ✅ OpenAI GPT-4o-mini | 100% (16/16) | 0.14 | 0.50 | 0.22 | 1.65s |
| ✅ Baseline (Local Heuristic) | 100% (16/16) | 1.00 | 0.25 | 0.40 | 0.00s |

### 🔍 Detailed Model Metrics

#### ✅ MedGemma (Hugging Face)

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.13 (detected issues / total detected)
- Issue Detection Recall: 0.50 (detected issues / expected issues)
- F1 Score: 0.21 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.481ms (effectively instant)
- Full Pipeline Time: 2.960s (2959.8ms)
- Processing Speed: 5.41 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ OpenAI GPT-4o-mini

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.14 (detected issues / total detected)
- Issue Detection Recall: 0.50 (detected issues / expected issues)
- F1 Score: 0.22 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.401ms (effectively instant)
- Full Pipeline Time: 1.654s (1654.5ms)
- Processing Speed: 9.67 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ Baseline (Local Heuristic)

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 1.00 (detected issues / total detected)
- Issue Detection Recall: 0.25 (detected issues / expected issues)
- F1 Score: 0.40 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.315ms (effectively instant)
- Full Pipeline Time: 0.459ms (effectively instant)
- Processing Speed: 34887.29 docs/sec

**💡 Token Usage:** N/A (local heuristic model)

---

**Note:** Issue detection metrics reflect performance against ground truth annotations. See `benchmarks/GROUND_TRUTH_SCHEMA.md` for annotation details.

_Run benchmarks: `python scripts/generate_benchmarks.py --model all`_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## 📊 Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents (medical bills, dental bills, EOBs, pharmacy receipts)._  
_Last updated: 2026-02-03 12:54:59_

### Model Performance Comparison

| Model | Success Rate | Precision | Recall | F1 Score | Avg Latency |
|-------|-------------|-----------|--------|----------|-------------|
| ✅ MedGemma (Hugging Face) | 100% (16/16) | 0.14 | 0.50 | 0.22 | 2.94s |
| ✅ OpenAI GPT-4o-mini | 100% (16/16) | 0.13 | 0.50 | 0.21 | 1.67s |
| ✅ Baseline (Local Heuristic) | 100% (16/16) | 1.00 | 0.25 | 0.40 | 0.00s |

### 🔍 Detailed Model Metrics

#### ✅ MedGemma (Hugging Face)

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.14 (detected issues / total detected)
- Issue Detection Recall: 0.50 (detected issues / expected issues)
- F1 Score: 0.22 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.514ms (effectively instant)
- Full Pipeline Time: 2.944s (2943.7ms)
- Processing Speed: 5.44 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ OpenAI GPT-4o-mini

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.13 (detected issues / total detected)
- Issue Detection Recall: 0.50 (detected issues / expected issues)
- F1 Score: 0.21 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.399ms (effectively instant)
- Full Pipeline Time: 1.673s (1672.6ms)
- Processing Speed: 9.57 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ Baseline (Local Heuristic)

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 1.00 (detected issues / total detected)
- Issue Detection Recall: 0.25 (detected issues / expected issues)
- F1 Score: 0.40 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.297ms (effectively instant)
- Full Pipeline Time: 0.403ms (effectively instant)
- Processing Speed: 39666.34 docs/sec

**💡 Token Usage:** N/A (local heuristic model)

---

**Note:** Issue detection metrics reflect performance against ground truth annotations. See `benchmarks/GROUND_TRUTH_SCHEMA.md` for annotation details.

_Run benchmarks: `python scripts/generate_benchmarks.py --model all`_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents._

### MedGemma Results

- **Extraction Accuracy**: 100.0%
- **Issue Detection Precision**: 0.00
- **Issue Detection Recall**: 0.00
- **Issue Detection F1 Score**: 0.00
- **JSON Validity Rate**: 100.0%
- **Avg Extraction Time**: 0.00s
- **Avg Full Pipeline Time**: 2.88s

_Generated: 2026-02-03 12:39:12_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents._

### OpenAI GPT-4o-mini Results

- **Extraction Accuracy**: 100.0%
- **Issue Detection Precision**: 0.12
- **Issue Detection Recall**: 0.50
- **Issue Detection F1 Score**: 0.19
- **JSON Validity Rate**: 100.0%
- **Avg Extraction Time**: 0.00s
- **Avg Full Pipeline Time**: 2.42s

_Generated: 2026-02-03 12:38:17_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents._

### Baseline (Local Heuristic) Results

- **Extraction Accuracy**: 100.0%
- **Issue Detection Precision**: 1.00
- **Issue Detection Recall**: 0.25
- **Issue Detection F1 Score**: 0.40
- **JSON Validity Rate**: 100.0%
- **Avg Extraction Time**: 0.00s
- **Avg Full Pipeline Time**: 0.00s

_Generated: 2026-02-03 12:37:32_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents._

### Baseline (Local Heuristic) Results

- **Extraction Accuracy**: 100.0%
- **Issue Detection Precision**: 0.00
- **Issue Detection Recall**: 0.00
- **Issue Detection F1 Score**: 0.00
- **JSON Validity Rate**: 100.0%
- **Avg Extraction Time**: 0.00s
- **Avg Full Pipeline Time**: 0.00s

_Generated: 2026-02-03 12:36:18_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents._

### OpenAI GPT-4o-mini Results

- **Extraction Accuracy**: 100.0%
- **Issue Detection Precision**: 0.00
- **Issue Detection Recall**: 0.00
- **Issue Detection F1 Score**: 0.00
- **JSON Validity Rate**: 100.0%
- **Avg Extraction Time**: 0.00s
- **Avg Full Pipeline Time**: 1.15s

_Generated: 2026-02-03 12:27:04_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents._

### OpenAI GPT-4o-mini Results

- **Extraction Accuracy**: 100.0%
- **Issue Detection Precision**: 0.00
- **Issue Detection Recall**: 0.00
- **Issue Detection F1 Score**: 0.00
- **JSON Validity Rate**: 100.0%
- **Avg Extraction Time**: 0.00s
- **Avg Full Pipeline Time**: 0.93s

_Generated: 2026-02-03 12:24:53_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents._

### Baseline (Local Heuristic) Results

- **Extraction Accuracy**: 100.0%
- **Issue Detection Precision**: 0.00
- **Issue Detection Recall**: 0.00
- **Issue Detection F1 Score**: 0.00
- **JSON Validity Rate**: 100.0%
- **Avg Extraction Time**: 0.00s
- **Avg Full Pipeline Time**: 0.00s

_Generated: 2026-02-03 12:23:52_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## 📊 Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents (medical bills, dental bills, EOBs, pharmacy receipts)._  
_Last updated: 2026-02-03 12:21:28_

### Model Performance Comparison

| Model | Success Rate | Precision | Recall | F1 Score | Avg Latency |
|-------|-------------|-----------|--------|----------|-------------|
| ⚠️ MedGemma (Hugging Face) | 81% (13/16) | 0.00 | 0.00 | 0.00 | 2.82s |
| ✅ OpenAI GPT-4o-mini | 100% (16/16) | 0.00 | 0.00 | 0.00 | 1.11s |
| ✅ Baseline (Local Heuristic) | 100% (16/16) | 0.00 | 0.00 | 0.00 | 0.00s |

### 🔍 Detailed Model Metrics

#### ⚠️ MedGemma (Hugging Face)

**📈 Accuracy Metrics:**
- Extraction Success: 81.2% (13/16 documents)
- JSON Validity: 81.2%
- Issue Detection Precision: 0.00 (detected issues / total detected)
- Issue Detection Recall: 0.00 (detected issues / expected issues)
- F1 Score: 0.00 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.622ms (effectively instant)
- Full Pipeline Time: 2.818s (2818.5ms)
- Processing Speed: 5.68 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ OpenAI GPT-4o-mini

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.00 (detected issues / total detected)
- Issue Detection Recall: 0.00 (detected issues / expected issues)
- F1 Score: 0.00 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.355ms (effectively instant)
- Full Pipeline Time: 1.110s (1110.3ms)
- Processing Speed: 14.41 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ Baseline (Local Heuristic)

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.00 (detected issues / total detected)
- Issue Detection Recall: 0.00 (detected issues / expected issues)
- F1 Score: 0.00 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.319ms (effectively instant)
- Full Pipeline Time: 0.322ms (effectively instant)
- Processing Speed: 49763.49 docs/sec

**💡 Token Usage:** N/A (local heuristic model)

---

**Note:** Issue detection metrics reflect performance against ground truth annotations. See `benchmarks/GROUND_TRUTH_SCHEMA.md` for annotation details.

_Run benchmarks: `python scripts/generate_benchmarks.py --model all`_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## 📊 Benchmark Analysis

_Evaluated on 16 synthetic healthcare billing documents (medical bills, dental bills, EOBs, pharmacy receipts)._  
_Last updated: 2026-02-03 12:02:50_

### Model Performance Comparison

| Model | Success Rate | Precision | Recall | F1 Score | Avg Latency |
|-------|-------------|-----------|--------|----------|-------------|
| ⚠️ MedGemma (Hugging Face) | 88% (14/16) | 0.00 | 0.00 | 0.00 | 2.88s |
| ✅ OpenAI GPT-4o-mini | 100% (16/16) | 0.00 | 0.00 | 0.00 | 1.28s |
| ✅ Baseline (Local Heuristic) | 100% (16/16) | 0.00 | 0.00 | 0.00 | 0.00s |

### 🔍 Detailed Model Metrics

#### ⚠️ MedGemma (Hugging Face)

**📈 Accuracy Metrics:**
- Extraction Success: 87.5% (14/16 documents)
- JSON Validity: 87.5%
- Issue Detection Precision: 0.00 (detected issues / total detected)
- Issue Detection Recall: 0.00 (detected issues / expected issues)
- F1 Score: 0.00 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.596ms (effectively instant)
- Full Pipeline Time: 2.876s (2876.3ms)
- Processing Speed: 5.56 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ OpenAI GPT-4o-mini

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.00 (detected issues / total detected)
- Issue Detection Recall: 0.00 (detected issues / expected issues)
- F1 Score: 0.00 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.443ms (effectively instant)
- Full Pipeline Time: 1.282s (1282.1ms)
- Processing Speed: 12.48 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ Baseline (Local Heuristic)

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (16/16 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.00 (detected issues / total detected)
- Issue Detection Recall: 0.00 (detected issues / expected issues)
- F1 Score: 0.00 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.323ms (effectively instant)
- Full Pipeline Time: 0.326ms (effectively instant)
- Processing Speed: 49048.39 docs/sec

**💡 Token Usage:** N/A (local heuristic model)

---

**Note:** Issue detection metrics reflect performance against ground truth annotations. See `benchmarks/GROUND_TRUTH_SCHEMA.md` for annotation details.

_Run benchmarks: `python scripts/generate_benchmarks.py --model all`_

<!-- BENCHMARK_SECTION_END -->

<!-- BENCHMARK_SECTION_START -->

## 📊 Benchmark Analysis

_Evaluated on 6 synthetic healthcare billing documents (medical bills, dental bills, EOBs, pharmacy receipts)._  
_Last updated: 2026-02-03 11:43:02_

### Model Performance Comparison

| Model | Success Rate | Precision | Recall | F1 Score | Avg Latency |
|-------|-------------|-----------|--------|----------|-------------|
| ✅ MedGemma (Hugging Face) | 100% (6/6) | 0.00 | 0.00 | 0.00 | 2.29s |
| ✅ OpenAI GPT-4o-mini | 100% (6/6) | 0.00 | 0.00 | 0.00 | 3.56s |
| ✅ Baseline (Local Heuristic) | 100% (6/6) | 0.00 | 0.00 | 0.00 | 0.00s |

### 🔍 Detailed Model Metrics

#### ✅ MedGemma (Hugging Face)

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (6/6 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.00 (detected issues / total detected)
- Issue Detection Recall: 0.00 (detected issues / expected issues)
- F1 Score: 0.00 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.656ms (effectively instant)
- Full Pipeline Time: 2.289s (2288.9ms)
- Processing Speed: 2.62 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ OpenAI GPT-4o-mini

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (6/6 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.00 (detected issues / total detected)
- Issue Detection Recall: 0.00 (detected issues / expected issues)
- F1 Score: 0.00 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.365ms (effectively instant)
- Full Pipeline Time: 3.563s (3562.7ms)
- Processing Speed: 1.68 docs/sec

**💡 Token Usage:** Not tracked (provider API limitation)

#### ✅ Baseline (Local Heuristic)

**📈 Accuracy Metrics:**
- Extraction Success: 100.0% (6/6 documents)
- JSON Validity: 100.0%
- Issue Detection Precision: 0.00 (detected issues / total detected)
- Issue Detection Recall: 0.00 (detected issues / expected issues)
- F1 Score: 0.00 (harmonic mean of precision/recall)

**⚡ Performance Metrics:**
- Extraction Time: 0.274ms (effectively instant)
- Full Pipeline Time: 0.277ms (effectively instant)
- Processing Speed: 21663.36 docs/sec

**💡 Token Usage:** N/A (local heuristic model)

---

**Note:** Issue detection metrics are currently zero because test documents lack ground truth issue annotations. Future benchmarks will include labeled test data.

_Run benchmarks: `python scripts/generate_benchmarks.py --model all`_

<!-- BENCHMARK_SECTION_END -->
