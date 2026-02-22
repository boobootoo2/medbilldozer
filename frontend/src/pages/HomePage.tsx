/**
 * Home page - Document upload and analysis
 */
import { useState, useRef, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Link as LinkIcon, FileText, ChevronDown, ChevronUp, Upload, Receipt, HeartPulse, ShieldCheck } from 'lucide-react';
import { UserMenu } from '../components/auth/UserMenu';
import { MultiFileUpload } from '../components/documents/MultiFileUpload';
import { DocumentList, DocumentListRef } from '../components/documents/DocumentList';
import { InsuranceConnectionModal } from '../components/insurance/InsuranceConnectionModal';
import { AnalysisProgress } from '../components/analysis/AnalysisProgress';
import { analysisService } from '../services/analysis.service';
import { documentsService } from '../services/documents.service';

interface MockDoc {
  name: string;
  format: 'PDF' | 'TXT' | 'PNG' | 'JPG';
  description: string;
  documentType: string;
  content: string;
}

interface MockCategory {
  id: string;
  label: string;
  icon: ReactNode;
  description: string;
  docs: MockDoc[];
}

const MOCK_CATEGORIES: MockCategory[] = [
  {
    id: 'bills',
    label: 'Medical Bills',
    icon: <Receipt className="w-5 h-5" />,
    description: 'Sample hospital bills and pharmacy receipts',
    docs: [
      {
        name: 'hospital-bill-sample.txt',
        format: 'TXT',
        description: 'ER visit with itemized charges and potential duplicate codes',
        documentType: 'medical_bill',
        content: `CITY GENERAL HOSPITAL
123 Medical Center Drive, Springfield, ST 12345
Tel: (555) 123-4567  |  Fax: (555) 123-4568

PATIENT STATEMENT
-----------------
Date Issued: 01/15/2024
Account #: PAT-20240115-001
Patient: Jane Doe
DOB: 03/15/1980
Insurance: BlueCross BlueShield ID: BX-987654321

SERVICES RENDERED - Date of Service: 01/10/2024
-----------------------------------------------
CPT 99283  Emergency Dept Visit (Moderate)       $850.00
CPT 71046  Chest X-Ray, 2 Views                  $320.00
CPT 71046  Chest X-Ray, 2 Views (DUPLICATE)      $320.00
CPT 93000  Electrocardiogram Routine ECG          $215.00
CPT 85025  Complete Blood Count (CBC)            $145.00
CPT 80053  Comprehensive Metabolic Panel          $210.00
CPT 96365  IV Infusion, Initial                  $475.00
CPT 99213  Office/Outpatient Visit Level 3        $180.00

                              SUBTOTAL:         $2,715.00
                   Insurance Adjustment:          -$543.00
                  AMOUNT DUE FROM PATIENT:       $2,172.00

NOTES: Please review line 3 - possible duplicate billing for X-Ray.
Payment due within 30 days. Contact billing@citygeneralhospital.com
`,
      },
      {
        name: 'pharmacy-receipt-sample.txt',
        format: 'TXT',
        description: 'Monthly prescription with potential overcharge',
        documentType: 'pharmacy_receipt',
        content: `WELLNESS PHARMACY
456 Main Street, Springfield, ST 12345
Tel: (555) 987-6543
Pharmacist: Dr. R. Patel, PharmD

PRESCRIPTION RECEIPT
--------------------
Date: 01/12/2024
Rx #: WP-2024-00892
Patient: Jane Doe  DOB: 03/15/1980
Insurance: BlueCross BlueShield BX-987654321

MEDICATIONS DISPENSED:
----------------------
Lisinopril 10mg Tablet                 30-day supply
  NDC: 68180-0513-01  Qty: 30         $15.00
  Insurance paid:                     -$10.00
  Your cost:                           $5.00

Atorvastatin 40mg Tablet               30-day supply
  NDC: 00071-0157-23  Qty: 30        $125.00
  Brand dispensed (generic available)
  Insurance paid:                     -$75.00
  Your cost:                          $50.00

Metformin 500mg Tablet                 90-day supply
  NDC: 00591-0469-01  Qty: 90         $42.00
  Insurance paid:                     -$30.00
  Your cost:                          $12.00

                        TOTAL DUE:    $67.00

NOTE: Generic Atorvastatin available at $8.00/month.
Ask your pharmacist about generic substitution options.
`,
      },
    ],
  },
  {
    id: 'health',
    label: 'Health History',
    icon: <HeartPulse className="w-5 h-5" />,
    description: 'Medical records, lab results, and visit summaries',
    docs: [
      {
        name: 'lab-results-sample.txt',
        format: 'TXT',
        description: 'Annual blood panel with flagged values',
        documentType: 'other',
        content: `SPRINGFIELD MEDICAL LABORATORY
789 Lab Drive, Springfield, ST 12345
CLIA #: 12D3456789

LABORATORY REPORT
-----------------
Patient: Jane Doe            DOB: 03/15/1980
MRN: MRN-20240001            Order Date: 01/08/2024
Ordering Provider: Dr. M. Chen, MD   Report Date: 01/09/2024
Insurance: BlueCross BX-987654321

COMPREHENSIVE METABOLIC PANEL (CPT 80053)
------------------------------------------
Glucose            92 mg/dL      [70-99]       NORMAL
BUN                18 mg/dL      [7-20]        NORMAL
Creatinine         0.9 mg/dL     [0.6-1.2]     NORMAL
eGFR               >60 mL/min                  NORMAL
Sodium             139 mmol/L    [136-145]     NORMAL
Potassium          3.4 mmol/L    [3.5-5.1]     LOW *
Chloride           101 mmol/L    [98-107]      NORMAL
CO2                24 mmol/L     [21-32]       NORMAL
Calcium            9.1 mg/dL     [8.5-10.2]    NORMAL
Total Protein      7.2 g/dL      [6.3-8.2]     NORMAL
Albumin            4.0 g/dL      [3.5-5.0]     NORMAL
AST                28 U/L        [10-40]       NORMAL
ALT                32 U/L        [7-40]        NORMAL

LIPID PANEL (CPT 80061)
-----------------------
Total Cholesterol  215 mg/dL     [<200]        HIGH *
LDL Cholesterol    138 mg/dL     [<100]        HIGH *
HDL Cholesterol     48 mg/dL     [>40]         NORMAL
Triglycerides      145 mg/dL     [<150]        NORMAL

COMPLETE BLOOD COUNT (CPT 85025)
----------------------------------
WBC                6.8 K/uL      [4.5-11.0]    NORMAL
RBC                4.5 M/uL      [4.1-5.1]     NORMAL
Hemoglobin         13.1 g/dL     [12.0-16.0]   NORMAL
Hematocrit         39.2%         [36-46]       NORMAL

* Abnormal values - physician follow-up recommended.
`,
      },
      {
        name: 'visit-summary-sample.txt',
        format: 'TXT',
        description: 'Primary care visit summary and treatment plan',
        documentType: 'other',
        content: `SPRINGFIELD FAMILY MEDICINE
321 Health Blvd, Springfield, ST 12345
Tel: (555) 246-8101

AFTER-VISIT SUMMARY
--------------------
Patient: Jane Doe           Date of Visit: 01/10/2024
Provider: Dr. M. Chen, MD   Visit Type: Annual Wellness Exam
MRN: MRN-20240001           Next Appt: 01/10/2025

REASON FOR VISIT:
Annual preventive care examination (CPT G0439)

VITAL SIGNS:
Height: 5'6"  Weight: 148 lbs  BMI: 23.9  BP: 122/78
Heart Rate: 72 bpm  Temp: 98.4°F  O2 Sat: 99%

ASSESSMENT & DIAGNOSES:
1. Hyperlipidemia (ICD-10: E78.5) - elevated LDL
2. Hypokalemia (ICD-10: E87.6) - mild, dietary
3. Preventive care, adult (ICD-10: Z00.00)

PLAN:
1. Start Atorvastatin 40mg daily for cholesterol
2. Increase dietary potassium (bananas, spinach, avocado)
3. Annual labs ordered for follow-up
4. Flu vaccination administered today
5. Return to clinic if symptoms develop

SERVICES BILLED:
CPT G0439 - Annual Wellness Visit    $250.00
CPT 90686 - Flu Vaccine              $45.00
CPT 90471 - Vaccine Administration   $25.00
`,
      },
    ],
  },
  {
    id: 'insurance',
    label: 'Insurance Documents',
    icon: <ShieldCheck className="w-5 h-5" />,
    description: 'EOBs, plan summaries, and coverage details',
    docs: [
      {
        name: 'eob-sample.txt',
        format: 'TXT',
        description: 'Explanation of Benefits showing claims processed',
        documentType: 'insurance_eob',
        content: `BLUECROSS BLUESHIELD
Explanation of Benefits (EOB)
P.O. Box 1000, Chicago, IL 60601

Member: Jane Doe                ID: BX-987654321
Group #: GRP-54321              Plan: PPO Gold Plus
EOB Date: 01/20/2024            Claim #: CLM-2024-00441

CLAIM DETAILS - Services by: City General Hospital
---------------------------------------------------
Date       Service              Billed    Allowed  Plan Paid  You Owe
01/10/24   ER Visit (99283)    $850.00   $680.00   $544.00   $136.00
01/10/24   Chest X-Ray(71046)  $320.00   $200.00   $160.00    $40.00
01/10/24   Chest X-Ray(71046)  $320.00   $200.00     $0.00   $200.00 *
01/10/24   ECG (93000)         $215.00   $160.00   $128.00    $32.00
01/10/24   CBC (85025)         $145.00   $100.00    $80.00    $20.00
01/10/24   Metabolic (80053)   $210.00   $155.00   $124.00    $31.00
01/10/24   IV Infusion (96365) $475.00   $350.00   $280.00    $70.00

                    TOTALS:  $2,535.00 $1,845.00 $1,316.00  $529.00

* CLAIM ADJUSTMENT: Second X-Ray claim (71046) denied - duplicate service.
  If you believe this is an error, contact member services to appeal.

DEDUCTIBLE STATUS: $250.00 applied / $1,500.00 annual deductible
OUT-OF-POCKET: $529.00 applied / $4,000.00 annual maximum

Questions? Call 1-800-555-2583 or visit bluecross.example.com
`,
      },
      {
        name: 'insurance-plan-summary.txt',
        format: 'TXT',
        description: '2024 benefits summary and coverage details',
        documentType: 'insurance_eob',
        content: `BLUECROSS BLUESHIELD
2024 PLAN SUMMARY - PPO GOLD PLUS
Member: Jane Doe  |  ID: BX-987654321  |  Effective: 01/01/2024

PLAN OVERVIEW
--------------
Plan Type:          Preferred Provider Organization (PPO)
Network:            BlueCard National Network
Primary Care:       No referral required
Specialist:         No referral required

COST SHARING (In-Network)
--------------------------
Annual Deductible:  $1,500 Individual / $3,000 Family
Out-of-Pocket Max:  $4,000 Individual / $8,000 Family
Coinsurance:        20% after deductible
Primary Care Visit: $25 copay (deductible waived)
Specialist Visit:   $50 copay (deductible waived)
Urgent Care:        $75 copay
Emergency Room:     $250 copay + 20% coinsurance

PRESCRIPTION DRUG COVERAGE
----------------------------
Tier 1 (Generic):         $10 copay
Tier 2 (Preferred Brand): $50 copay
Tier 3 (Non-Preferred):   $100 copay
Tier 4 (Specialty):       30% coinsurance

PREVENTIVE CARE (In-Network, No Cost)
---------------------------------------
Annual wellness exam, vaccinations, cancer screenings,
blood pressure/cholesterol checks, and diabetes screening.

MENTAL HEALTH & SUBSTANCE ABUSE
---------------------------------
In-Network: $25 copay (same as primary care)
Telehealth: $0 copay for first 3 visits/year

Customer Service: 1-800-555-2583
`,
      },
    ],
  },
];

export const HomePage = () => {
  const navigate = useNavigate();
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [showInsuranceModal, setShowInsuranceModal] = useState(false);
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(null);
  const documentListRef = useRef<DocumentListRef>(null);
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});
  const [uploadingDoc, setUploadingDoc] = useState<string | null>(null);

  const toggleSection = (id: string) => {
    setOpenSections(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleDemoUpload = async (doc: MockDoc) => {
    const key = doc.name;
    setUploadingDoc(key);
    try {
      const blob = new Blob([doc.content], { type: 'text/plain' });
      const file = new File([blob], doc.name, { type: 'text/plain' });
      await documentsService.uploadDocument(file, doc.documentType);
      await handleUploadComplete();
      alert(`Demo document "${doc.name}" uploaded successfully!`);
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploadingDoc(null);
    }
  };

  const handleDocumentSelect = (documentId: string) => {
    setSelectedDocuments(prev =>
      prev.includes(documentId)
        ? prev.filter(id => id !== documentId)
        : [...prev, documentId]
    );
  };

  const handleUploadComplete = async () => {
    console.log('📤 HomePage: Upload complete, waiting briefly for DB commit...');
    // Small delay to ensure database transaction completes
    await new Promise(resolve => setTimeout(resolve, 500));
    console.log('🔄 HomePage: Now refreshing document list...');
    console.log('📍 HomePage: documentListRef.current =', documentListRef.current);

    if (!documentListRef.current) {
      console.error('❌ HomePage: documentListRef.current is null! Ref not attached.');
      return;
    }

    await documentListRef.current.refresh();
    console.log('✅ HomePage: Document list refresh complete');
  };

  const handleAnalyze = async () => {
    if (selectedDocuments.length === 0) {
      alert('Please select at least one document to analyze');
      return;
    }

    try {
      setAnalyzing(true);
      const { analysis_id } = await analysisService.triggerAnalysis(
        selectedDocuments,
        'medgemma-ensemble'
      );

      // Show analysis progress inline (no navigation)
      setCurrentAnalysisId(analysis_id);
    } catch (err: any) {
      alert('Failed to start analysis: ' + err.message);
      setAnalyzing(false);
    }
  };

  const handleBackToDocuments = async () => {
    setCurrentAnalysisId(null);
    setAnalyzing(false);
    setSelectedDocuments([]);
    await documentListRef.current?.refresh();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">MedBillDozer</h1>
            <p className="text-sm text-gray-600">AI-Powered Medical Billing Analysis</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/documents')}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors font-medium"
            >
              <FileText className="w-5 h-5" />
              Manage Documents
            </button>
            <UserMenu />
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Show Analysis Progress when analyzing */}
        {currentAnalysisId ? (
          <AnalysisProgress
            analysisId={currentAnalysisId}
            onBack={handleBackToDocuments}
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column - Upload */}
            <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Documents</h2>
              <p className="text-gray-600">
                Upload medical bills, insurance EOBs, or receipts for analysis
              </p>
            </div>
            <MultiFileUpload onUploadComplete={async (documentIds) => {
              await handleUploadComplete();
              // Show success message
              if (documentIds.length > 0) {
                alert(`Successfully uploaded ${documentIds.length} document(s)!`);
              }
            }} />

            {/* Insurance Connection Button */}
            <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
                  <LinkIcon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    Connect Insurance or Provider (Demo)
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    See what automatic data import would look like
                  </p>
                  <button
                    onClick={() => setShowInsuranceModal(true)}
                    className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View Demo Integration
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Documents & Analysis */}
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Documents</h2>
                <p className="text-gray-600">
                  Select documents to analyze for billing errors
                </p>
              </div>
              {selectedDocuments.length > 0 && (
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {analyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Play size={20} />
                      Analyze ({selectedDocuments.length})
                    </>
                  )}
                </button>
              )}
            </div>

            <DocumentList
              ref={documentListRef}
              onDocumentSelect={handleDocumentSelect}
              selectedDocuments={selectedDocuments}
            />
          </div>
        </div>
        )}

        {/* Features - Only show when not analyzing */}
        {!currentAnalysisId && (
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🤖</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Analysis</h3>
            <p className="text-gray-600 text-sm">
              MedGemma-ensemble analyzes bills using medical domain expertise
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">💰</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Find Savings</h3>
            <p className="text-gray-600 text-sm">
              Detect overcharges, duplicate billing, and coding errors
            </p>
          </div>

          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Cross-Document</h3>
            <p className="text-gray-600 text-sm">
              Analyze multiple bills together to find duplicate payments
            </p>
          </div>
        </div>
        )}

        {/* Sample Documents Accordion - Only show when not analyzing */}
        {!currentAnalysisId && (
          <div className="mt-12">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-gray-900">Sample Documents for Testing</h2>
              <p className="text-sm text-gray-600 mt-1">
                Upload realistic mock documents to explore the analysis features
              </p>
            </div>

            <div className="space-y-3">
              {MOCK_CATEGORIES.map(category => (
                <div key={category.id} className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                  {/* Accordion Header */}
                  <button
                    onClick={() => toggleSection(category.id)}
                    className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors text-left"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600 flex-shrink-0">
                        {category.icon}
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">{category.label}</p>
                        <p className="text-xs text-gray-500">{category.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-xs text-gray-400">{category.docs.length} samples</span>
                      {openSections[category.id]
                        ? <ChevronUp className="w-5 h-5 text-gray-400" />
                        : <ChevronDown className="w-5 h-5 text-gray-400" />
                      }
                    </div>
                  </button>

                  {/* Accordion Body */}
                  {openSections[category.id] && (
                    <div className="border-t border-gray-100 divide-y divide-gray-100">
                      {category.docs.map(doc => (
                        <div key={doc.name} className="flex items-center justify-between px-5 py-3 bg-gray-50 hover:bg-gray-100 transition-colors">
                          <div className="flex items-center gap-3 min-w-0">
                            <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
                            <div className="min-w-0">
                              <p className="text-sm font-medium text-gray-800 truncate">{doc.name}</p>
                              <p className="text-xs text-gray-500">{doc.description}</p>
                            </div>
                            <span className="flex-shrink-0 px-2 py-0.5 bg-gray-200 text-gray-600 text-xs font-medium rounded">
                              {doc.format}
                            </span>
                          </div>
                          <button
                            onClick={() => handleDemoUpload(doc)}
                            disabled={uploadingDoc === doc.name}
                            className="ml-4 flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {uploadingDoc === doc.name ? (
                              <>
                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white" />
                                Uploading...
                              </>
                            ) : (
                              <>
                                <Upload className="w-3 h-3" />
                                Upload Demo
                              </>
                            )}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Insurance Connection Modal */}
      <InsuranceConnectionModal
        isOpen={showInsuranceModal}
        onClose={() => setShowInsuranceModal(false)}
        onConnect={(providerId) => {
          console.log('Connected to:', providerId);
          alert(`Demo: Successfully connected to ${providerId}. In production, this would import your medical bills and claims automatically.`);
          setShowInsuranceModal(false);
        }}
      />
    </div>
  );
};
