"""
Multimodal Analysis Service
Coordinates multi-document and multi-modal (text + images) medical billing analysis
Detects both billing errors and clinical inconsistencies
"""

import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import logging

from app.services.storage_service import StorageService
from medbilldozer.core.clinical_validator import ClinicalValidator
from medbilldozer.core.orchestrator_agent import OrchestratorAgent
from medbilldozer.providers.provider_registry import register_providers, ProviderRegistry

logger = logging.getLogger(__name__)


class MultimodalAnalysisService:
    """
    Comprehensive multimodal analysis service
    Handles text documents (bills, EOBs) and images (X-rays, prescriptions)
    """

    def __init__(self):
        self.storage_service = StorageService()
        self.clinical_validator = ClinicalValidator(model="gpt-4o-mini")
        # Register providers on initialization
        register_providers()

    async def analyze_documents(
        self,
        document_ids: List[str],
        user_id: str,
        provider: str = "medgemma-ensemble"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive multimodal analysis on multiple documents

        Args:
            document_ids: List of document IDs to analyze
            user_id: User ID for authentication
            provider: LLM provider to use (default: medgemma-ensemble)

        Returns:
            Comprehensive analysis results with billing and clinical findings
        """
        logger.info(f"Starting multimodal analysis for {len(document_ids)} documents")

        # Step 1: Download and categorize documents
        documents = await self._download_documents(document_ids, user_id)
        text_docs = [d for d in documents if d['type'] == 'text']
        image_docs = [d for d in documents if d['type'] == 'image']

        logger.info(f"Categorized: {len(text_docs)} text docs, {len(image_docs)} image docs")

        # Step 2: Analyze text documents (bills, EOBs)
        text_analysis = await self._analyze_text_documents(text_docs, provider)

        # Step 3: Analyze images (X-rays, prescriptions, clinical photos)
        image_analysis = await self._analyze_images(image_docs)

        # Step 4: Cross-reference findings
        cross_reference = await self._cross_reference_findings(
            text_analysis,
            image_analysis,
            text_docs,
            image_docs
        )

        # Step 5: Compile comprehensive results
        results = self._compile_results(
            text_analysis,
            image_analysis,
            cross_reference
        )

        logger.info("Multimodal analysis complete")
        return results

    async def _download_documents(
        self,
        document_ids: List[str],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Download documents from storage and categorize"""
        documents = []

        for doc_id in document_ids:
            try:
                # Download document content
                content = await self.storage_service.download_document(doc_id, user_id)

                # Determine document type
                doc_type = self._classify_document_type(content)

                documents.append({
                    'id': doc_id,
                    'type': doc_type,
                    'content': content,
                    'path': content.get('path') if isinstance(content, dict) else None
                })
            except Exception as e:
                logger.error(f"Failed to download document {doc_id}: {e}")

        return documents

    def _classify_document_type(self, content: Any) -> str:
        """Classify document as text or image"""
        if isinstance(content, dict):
            content_type = content.get('content_type', '')
            if content_type.startswith('image/'):
                return 'image'
        return 'text'

    async def _analyze_text_documents(
        self,
        documents: List[Dict[str, Any]],
        provider: str
    ) -> Dict[str, Any]:
        """Analyze text documents for billing errors"""
        if not documents:
            return {
                'issues': [],
                'codes': [],
                'procedures': [],
                'diagnoses': []
            }

        # Use orchestrator for comprehensive analysis
        orchestrator = OrchestratorAgent(
            llm_provider=ProviderRegistry.get(provider)
        )

        all_issues = []
        all_codes = []
        all_procedures = []
        all_diagnoses = []

        for doc in documents:
            try:
                # Extract text content
                text = doc['content']
                if isinstance(text, dict):
                    text = text.get('text', '')

                # Run analysis
                result = orchestrator.run(text)

                all_issues.extend(result.get('issues', []))
                all_codes.extend(result.get('procedure_codes', []))
                all_procedures.extend(result.get('procedures', []))
                all_diagnoses.extend(result.get('diagnoses', []))

            except Exception as e:
                logger.error(f"Failed to analyze text document {doc['id']}: {e}")

        return {
            'issues': all_issues,
            'codes': all_codes,
            'procedures': all_procedures,
            'diagnoses': all_diagnoses
        }

    async def _analyze_images(
        self,
        image_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze medical images for clinical findings"""
        if not image_docs:
            return {'findings': []}

        findings = []

        for img_doc in image_docs:
            try:
                # Save image to temporary file
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    tmp.write(img_doc['content'])
                    tmp_path = Path(tmp.name)

                # Analyze image with clinical validator
                analysis_prompt = """
                Analyze this medical image and provide:
                1. What type of medical image is this? (X-ray, MRI, prescription, clinical photo, etc.)
                2. What body part or condition is shown?
                3. What diagnosis or findings are evident?
                4. What procedures or treatments would be appropriate?
                5. What CPT/ICD-10 codes would be relevant?
                6. Are there any clinical red flags or concerns?

                Be specific and use medical terminology.
                """

                result = self.clinical_validator.validate(
                    image_path=tmp_path,
                    context=analysis_prompt
                )

                findings.append({
                    'document_id': img_doc['id'],
                    'image_type': self._extract_image_type(result),
                    'body_part': self._extract_body_part(result),
                    'findings': result.get('findings', ''),
                    'recommended_codes': self._extract_codes(result),
                    'recommended_procedures': self._extract_procedures(result),
                    'clinical_flags': self._extract_flags(result),
                    'raw_analysis': result
                })

                # Cleanup
                tmp_path.unlink()

            except Exception as e:
                logger.error(f"Failed to analyze image {img_doc['id']}: {e}")
                findings.append({
                    'document_id': img_doc['id'],
                    'error': str(e)
                })

        return {'findings': findings}

    async def _cross_reference_findings(
        self,
        text_analysis: Dict[str, Any],
        image_analysis: Dict[str, Any],
        text_docs: List[Dict[str, Any]],
        image_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Cross-reference text and image findings to detect inconsistencies"""
        inconsistencies = []

        # Extract billed procedures and diagnoses from text
        billed_codes = set(text_analysis.get('codes', []))
        billed_diagnoses = set(text_analysis.get('diagnoses', []))
        billed_procedures = set(text_analysis.get('procedures', []))

        # Compare with image findings
        for finding in image_analysis.get('findings', []):
            if 'error' in finding:
                continue

            # Check if image findings match billed items
            img_codes = set(finding.get('recommended_codes', []))
            img_procedures = set(finding.get('recommended_procedures', []))

            # Detect code mismatches
            missing_codes = img_codes - billed_codes
            if missing_codes:
                inconsistencies.append({
                    'type': 'MISSING_PROCEDURE_CODE',
                    'severity': 'high',
                    'description': f'Image shows evidence for codes {missing_codes} but they were not billed',
                    'image_doc_id': finding['document_id'],
                    'image_type': finding.get('image_type'),
                    'recommended_action': 'Add missing procedure codes to billing'
                })

            # Detect procedure mismatches
            extra_billed = billed_procedures - img_procedures
            if extra_billed:
                inconsistencies.append({
                    'type': 'UNBILLED_PROCEDURE_MISMATCH',
                    'severity': 'high',
                    'description': f'Billed for {extra_billed} but image does not support this',
                    'image_doc_id': finding['document_id'],
                    'image_type': finding.get('image_type'),
                    'recommended_action': 'Review procedure billing for accuracy'
                })

            # Check clinical flags
            if finding.get('clinical_flags'):
                for flag in finding['clinical_flags']:
                    inconsistencies.append({
                        'type': 'CLINICAL_FLAG',
                        'severity': 'critical',
                        'description': f'Clinical concern identified in image: {flag}',
                        'image_doc_id': finding['document_id'],
                        'recommended_action': 'Review with medical professional'
                    })

        return {
            'inconsistencies': inconsistencies,
            'summary': {
                'total_inconsistencies': len(inconsistencies),
                'high_severity': len([i for i in inconsistencies if i['severity'] == 'high']),
                'critical': len([i for i in inconsistencies if i['severity'] == 'critical'])
            }
        }

    def _compile_results(
        self,
        text_analysis: Dict[str, Any],
        image_analysis: Dict[str, Any],
        cross_reference: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile comprehensive analysis results"""

        # Combine all issues
        all_issues = []

        # Add billing issues from text
        all_issues.extend([
            {**issue, 'source': 'billing_document', 'error_type': 'billing'}
            for issue in text_analysis.get('issues', [])
        ])

        # Add clinical inconsistencies
        all_issues.extend([
            {**inconsistency, 'source': 'cross_reference', 'error_type': 'clinical'}
            for inconsistency in cross_reference.get('inconsistencies', [])
        ])

        # Calculate total potential savings
        total_savings = sum(
            issue.get('potential_savings', 0)
            for issue in all_issues
            if 'potential_savings' in issue
        )

        return {
            'analysis_type': 'multimodal',
            'documents_analyzed': {
                'text': len(text_analysis.get('codes', [])),
                'images': len(image_analysis.get('findings', []))
            },
            'issues': all_issues,
            'billing_issues': [i for i in all_issues if i['error_type'] == 'billing'],
            'clinical_issues': [i for i in all_issues if i['error_type'] == 'clinical'],
            'cross_reference': cross_reference,
            'image_findings': image_analysis.get('findings', []),
            'procedure_codes': text_analysis.get('codes', []),
            'diagnoses': text_analysis.get('diagnoses', []),
            'total_potential_savings': total_savings,
            'summary': {
                'total_issues': len(all_issues),
                'billing_errors': len([i for i in all_issues if i['error_type'] == 'billing']),
                'clinical_concerns': len([i for i in all_issues if i['error_type'] == 'clinical']),
                'critical_flags': len([
                    i for i in all_issues
                    if i.get('severity') == 'critical'
                ])
            }
        }

    # Helper methods for extracting structured data from vision model responses
    def _extract_image_type(self, result: Dict[str, Any]) -> str:
        """Extract image type from analysis"""
        text = result.get('findings', '').lower()
        if 'x-ray' in text or 'xray' in text:
            return 'X-ray'
        elif 'mri' in text:
            return 'MRI'
        elif 'ct' in text or 'scan' in text:
            return 'CT Scan'
        elif 'prescription' in text or 'rx' in text:
            return 'Prescription'
        elif 'ultrasound' in text:
            return 'Ultrasound'
        return 'Clinical Image'

    def _extract_body_part(self, result: Dict[str, Any]) -> Optional[str]:
        """Extract body part from analysis"""
        text = result.get('findings', '').lower()
        body_parts = [
            'chest', 'lung', 'heart', 'abdomen', 'spine', 'knee', 'shoulder',
            'head', 'brain', 'pelvis', 'hand', 'foot', 'leg', 'arm'
        ]
        for part in body_parts:
            if part in text:
                return part.capitalize()
        return None

    def _extract_codes(self, result: Dict[str, Any]) -> List[str]:
        """Extract medical codes from analysis"""
        # Simple regex matching for common code formats
        import re
        text = result.get('findings', '')

        # CPT codes (5 digits)
        cpt_codes = re.findall(r'\b\d{5}\b', text)

        # ICD-10 codes (letter followed by digits)
        icd_codes = re.findall(r'\b[A-Z]\d{2}(?:\.\d{1,2})?\b', text)

        return list(set(cpt_codes + icd_codes))

    def _extract_procedures(self, result: Dict[str, Any]) -> List[str]:
        """Extract procedure names from analysis"""
        text = result.get('findings', '')
        # Look for common medical procedure keywords
        procedures = []
        procedure_keywords = [
            'surgery', 'scan', 'imaging', 'injection', 'examination',
            'biopsy', 'therapy', 'treatment', 'procedure'
        ]

        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in procedure_keywords):
                procedures.append(sentence.strip())

        return procedures[:5]  # Limit to 5 most relevant

    def _extract_flags(self, result: Dict[str, Any]) -> List[str]:
        """Extract clinical flags from analysis"""
        text = result.get('findings', '').lower()
        flags = []

        flag_keywords = [
            'concern', 'abnormal', 'suspicious', 'urgent', 'critical',
            'immediate attention', 'emergency', 'severe', 'acute'
        ]

        for keyword in flag_keywords:
            if keyword in text:
                # Extract sentence containing the keyword
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence:
                        flags.append(sentence.strip().capitalize())
                        break

        return list(set(flags))[:3]  # Limit to 3 most important flags
