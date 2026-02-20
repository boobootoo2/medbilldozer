"""
FHIR R4 client for insurance payer APIs.

This service handles:
- Patient demographics retrieval
- Coverage/benefits information
- Claims (ExplanationOfBenefit) retrieval
- FHIR resource parsing
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class FHIRClient:
    """
    FHIR R4 client for insurance payer APIs.

    Supports CMS-mandated FHIR endpoints for major payers:
    - UnitedHealthcare
    - Anthem/Elevance
    - Aetna
    - Cigna
    - Humana
    - Blue Cross Blue Shield

    Usage:
        fhir = FHIRClient("uhc", access_token)
        patient_data = await fhir.get_patient_demographics()
        claims = await fhir.get_explanation_of_benefits(patient_id)
    """

    # FHIR base URLs by payer (update with actual URLs from payer docs)
    PAYER_ENDPOINTS = {
        "uhc": os.getenv("UHC_FHIR_BASE_URL", "https://fhir.uhc.com/r4"),
        "anthem": os.getenv("ANTHEM_FHIR_BASE_URL", "https://fhir.anthem.com/r4"),
        "aetna": os.getenv("AETNA_FHIR_BASE_URL", "https://fhir.aetna.com/r4"),
        "cigna": os.getenv("CIGNA_FHIR_BASE_URL", "https://fhir.cigna.com/r4"),
        "humana": os.getenv("HUMANA_FHIR_BASE_URL", "https://fhir.humana.com/r4"),
        "bcbs": os.getenv("BCBS_FHIR_BASE_URL", "https://fhir.bcbs.com/r4"),
    }

    def __init__(self, payer_id: str, access_token: str):
        """
        Initialize FHIR client.

        Args:
            payer_id: Payer identifier (e.g., "uhc", "anthem")
            access_token: OAuth access token

        Raises:
            ValueError: If payer_id is not supported
        """
        self.payer_id = payer_id
        self.access_token = access_token
        self.base_url = self.PAYER_ENDPOINTS.get(payer_id)

        if not self.base_url:
            raise ValueError(f"Unsupported payer: {payer_id}")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/fhir+json",
                "Content-Type": "application/fhir+json",
            },
            timeout=30.0,
        )

        logger.info(f"Initialized FHIR client for {payer_id}")

    async def get_patient_demographics(self) -> Dict[str, Any]:
        """
        Retrieve patient demographics.

        FHIR Resource: Patient
        Endpoint: GET /Patient

        Returns:
            Patient resource (FHIR R4 format)

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        try:
            response = await self.client.get("/Patient")
            response.raise_for_status()

            data = response.json()
            logger.info(f"Retrieved patient demographics for {self.payer_id}")

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get patient demographics: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting patient demographics: {e}")
            raise

    async def get_coverage(self, patient_id: str) -> Dict[str, Any]:
        """
        Retrieve patient coverage details.

        FHIR Resource: Coverage
        Endpoint: GET /Coverage?patient={patient_id}

        Args:
            patient_id: FHIR Patient ID

        Returns:
            Bundle of Coverage resources

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        try:
            response = await self.client.get("/Coverage", params={"patient": patient_id})
            response.raise_for_status()

            data = response.json()
            logger.info(f"Retrieved coverage for patient {patient_id}")

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get coverage: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting coverage: {e}")
            raise

    async def get_explanation_of_benefits(
        self, patient_id: str, start_date: Optional[datetime] = None, count: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve claims (ExplanationOfBenefit resources).

        FHIR Resource: ExplanationOfBenefit
        Endpoint: GET /ExplanationOfBenefit?patient={patient_id}&_sort=-created

        Args:
            patient_id: FHIR Patient ID
            start_date: Only retrieve claims after this date (default: 6 months ago)
            count: Maximum number of claims to retrieve (default: 50)

        Returns:
            List of ExplanationOfBenefit resources

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        try:
            # Default to 6 months ago if no start_date provided
            if start_date is None:
                start_date = datetime.utcnow() - timedelta(days=180)

            params = {
                "patient": patient_id,
                "_sort": "-created",
                "_count": count,
                "created": f"ge{start_date.isoformat()}",
            }

            response = await self.client.get("/ExplanationOfBenefit", params=params)
            response.raise_for_status()

            data = response.json()
            entries = data.get("entry", [])

            logger.info(f"Retrieved {len(entries)} claims for patient {patient_id}")

            return entries

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get explanation of benefits: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting EOBs: {e}")
            raise

    async def get_provider_directory(
        self,
        name: Optional[str] = None,
        specialty: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search provider directory.

        FHIR Resource: Practitioner, Organization
        Endpoint: GET /Practitioner?name={name}

        Args:
            name: Provider name (partial match)
            specialty: Provider specialty
            location: Location (city, state, zip)

        Returns:
            List of Practitioner resources

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        try:
            params = {}
            if name:
                params["name"] = name
            if specialty:
                params["specialty"] = specialty
            if location:
                params["address"] = location

            response = await self.client.get("/Practitioner", params=params)
            response.raise_for_status()

            data = response.json()
            entries = data.get("entry", [])

            logger.info(f"Found {len(entries)} providers")

            return entries

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to search provider directory: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error searching providers: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info(f"Closed FHIR client for {self.payer_id}")

    # ========================================================================
    # FHIR Resource Parsers
    # ========================================================================

    @staticmethod
    def extract_member_id(patient_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract member ID from FHIR Patient resource.

        Args:
            patient_data: FHIR Patient resource

        Returns:
            Member ID or None if not found
        """
        identifiers = patient_data.get("identifier", [])

        for identifier in identifiers:
            # Look for member ID identifier type
            id_type = identifier.get("type", {})
            type_text = id_type.get("text", "").lower()

            if "member" in type_text or "subscriber" in type_text:
                return identifier.get("value")

            # Check coding
            codings = id_type.get("coding", [])
            for coding in codings:
                if "member" in coding.get("display", "").lower():
                    return identifier.get("value")

        # Fallback: return first identifier
        if identifiers:
            return identifiers[0].get("value")

        return None

    @staticmethod
    def parse_coverage_resource(coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse FHIR Coverage resource to extract benefits.

        Args:
            coverage_data: FHIR Coverage resource

        Returns:
            Parsed benefits data
        """
        # Extract deductible and OOP max from costToBeneficiary
        benefits = {
            "deductible_individual": None,
            "deductible_family": None,
            "oop_max_individual": None,
            "oop_max_family": None,
            "copays": {},
        }

        cost_to_beneficiary = coverage_data.get("costToBeneficiary", [])

        for cost_item in cost_to_beneficiary:
            cost_type = cost_item.get("type", {}).get("coding", [{}])[0].get("code")
            value = cost_item.get("valueMoney", {}).get("value")

            if cost_type == "deductible":
                benefits["deductible_individual"] = value
            elif cost_type == "maxoutofpocket":
                benefits["oop_max_individual"] = value

        return benefits

    @staticmethod
    def parse_eob_resource(eob_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse FHIR ExplanationOfBenefit resource to extract claim data.

        Args:
            eob_data: FHIR ExplanationOfBenefit resource

        Returns:
            Parsed claim data
        """
        resource = eob_data.get("resource", {})

        # Extract basic claim info
        claim = {
            "claim_number": resource.get("id"),
            "service_date": None,
            "provider_name": None,
            "provider_npi": None,
            "billed_amount": 0.0,
            "allowed_amount": 0.0,
            "paid_by_insurance": 0.0,
            "patient_responsibility": 0.0,
            "claim_status": resource.get("status"),
            "procedure_codes": [],
            "diagnosis_codes": [],
            "raw_data": resource,
        }

        # Extract service date
        period = resource.get("billablePeriod", {})
        claim["service_date"] = period.get("start") or period.get("end")

        # Extract provider info
        provider = resource.get("provider", {})
        if provider:
            claim["provider_name"] = provider.get("display")
            provider_id = provider.get("identifier", {})
            if provider_id:
                claim["provider_npi"] = provider_id.get("value")

        # Extract amounts
        total = resource.get("total", [])
        for total_item in total:
            category = total_item.get("category", {}).get("coding", [{}])[0].get("code")
            amount = total_item.get("amount", {}).get("value", 0.0)

            if category == "submitted":
                claim["billed_amount"] = amount
            elif category == "benefit":
                claim["paid_by_insurance"] = amount
            elif category == "eligible":
                claim["allowed_amount"] = amount

        # Extract patient responsibility
        benefit_balance = resource.get("benefitBalance", [])
        for balance in benefit_balance:
            financial = balance.get("financial", [])
            for fin_item in financial:
                fin_type = fin_item.get("type", {}).get("coding", [{}])[0].get("code")
                if fin_type == "copay":
                    claim["patient_responsibility"] += fin_item.get("usedMoney", {}).get(
                        "value", 0.0
                    )

        # Extract procedure codes
        items = resource.get("item", [])
        for item in items:
            procedure_code = item.get("productOrService", {}).get("coding", [{}])[0].get("code")
            if procedure_code:
                claim["procedure_codes"].append(procedure_code)

        # Extract diagnosis codes
        diagnoses = resource.get("diagnosis", [])
        for diagnosis in diagnoses:
            diagnosis_code = (
                diagnosis.get("diagnosisCodeableConcept", {}).get("coding", [{}])[0].get("code")
            )
            if diagnosis_code:
                claim["diagnosis_codes"].append(diagnosis_code)

        return claim


# ========================================================================
# Utility Functions
# ========================================================================


def is_fhir_supported(payer_id: str) -> bool:
    """
    Check if payer supports FHIR API.

    Args:
        payer_id: Payer identifier

    Returns:
        True if FHIR is supported
    """
    return payer_id in FHIRClient.PAYER_ENDPOINTS


def get_supported_payers() -> List[str]:
    """
    Get list of payers with FHIR support.

    Returns:
        List of payer IDs
    """
    return list(FHIRClient.PAYER_ENDPOINTS.keys())
