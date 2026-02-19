"""
Clinical Validator
Wrapper for automatic AI image validation using existing vision APIs
"""

import base64
import os
from pathlib import Path
from typing import Dict, Optional
from openai import OpenAI
import google.generativeai as genai


class ClinicalValidator:
    """Wrapper for clinical image validation using vision APIs"""

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize validator

        Args:
            model: Vision model to use (gpt-4o-mini, gemini-2.0-flash-exp)
        """
        self.model = model
        self.openai_client = None
        self.genai_model = None

        # Initialize API clients
        if model.startswith("gpt-"):
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        elif model.startswith("gemini-"):
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.genai_model = genai.GenerativeModel(model)

    def encode_image_to_base64(self, image_path: Path) -> str:
        """Encode image file to base64 string"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def get_media_type(self, image_path: Path) -> str:
        """Get media type from file extension"""
        ext = image_path.suffix.lower()
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return media_types.get(ext, 'image/png')

    def create_validation_prompt(
        self,
        clinical_finding: str,
        prescribed_treatment: str,
        patient_context: Optional[Dict] = None
    ) -> str:
        """
        Create clinical validation prompt

        Args:
            clinical_finding: Expected clinical finding from the image
            prescribed_treatment: Treatment that was prescribed
            patient_context: Optional patient demographics and context

        Returns:
            Formatted prompt for vision model
        """
        prompt = f"""You are a medical expert reviewing a clinical case for billing compliance.

**Clinical Finding (from imaging report):** {clinical_finding}

**Prescribed Treatment:** {prescribed_treatment}
"""

        if patient_context:
            prompt += f"""
**Patient Context:**
- Age: {patient_context.get('age', 'N/A')}
- Gender: {patient_context.get('gender', 'N/A')}
- Chief Complaint: {patient_context.get('chief_complaint', 'N/A')}
- Vital Signs: {patient_context.get('vital_signs', 'N/A')}
"""

        prompt += """
**Task:** Determine if the prescribed treatment is appropriate given the imaging findings.

Analyze the medical image and determine:
1. Does the image support the clinical finding described?
2. Is the prescribed treatment medically appropriate for these findings?
3. Are there any signs of overtreatment, undertreatment, or unnecessary procedures?

**Respond with:**
- "CORRECT" if the treatment matches the imaging findings appropriately
- "ERROR" if the treatment does not match or is inappropriate

Provide a brief justification (2-3 sentences) explaining your determination.

Format your response as:
DETERMINATION: [CORRECT or ERROR]
CONFIDENCE: [High/Medium/Low]
JUSTIFICATION: [Your explanation]
"""
        return prompt

    def call_openai_vision(self, image_path: Path, prompt: str) -> str:
        """Call OpenAI vision API"""
        if not self.openai_client:
            return "ERROR: OpenAI API key not configured"

        try:
            base64_image = self.encode_image_to_base64(image_path)
            media_type = self.get_media_type(image_path)

            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"ERROR: {str(e)}"

    def call_gemini_vision(self, image_path: Path, prompt: str) -> str:
        """Call Gemini vision API"""
        if not self.genai_model:
            return "ERROR: Gemini API key not configured"

        try:
            # Read image bytes
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Create parts for Gemini
            parts = [prompt, {"mime_type": self.get_media_type(image_path), "data": image_data}]

            response = self.genai_model.generate_content(parts)
            return response.text

        except Exception as e:
            return f"ERROR: {str(e)}"

    def validate_treatment(
        self,
        image_path: Path,
        clinical_finding: str,
        prescribed_treatment: str,
        patient_context: Optional[Dict] = None
    ) -> Dict:
        """
        Validate if prescribed treatment matches clinical findings

        Args:
            image_path: Path to medical image
            clinical_finding: Expected clinical finding
            prescribed_treatment: Prescribed treatment
            patient_context: Optional patient demographics

        Returns:
            {
                "is_appropriate": bool,
                "confidence": str,  # High, Medium, Low
                "justification": str,
                "model_response": str,
                "determination": str  # CORRECT or ERROR
            }
        """
        # Create prompt
        prompt = self.create_validation_prompt(
            clinical_finding,
            prescribed_treatment,
            patient_context
        )

        # Call appropriate vision API
        if self.model.startswith("gpt-"):
            response = self.call_openai_vision(image_path, prompt)
        elif self.model.startswith("gemini-"):
            response = self.call_gemini_vision(image_path, prompt)
        else:
            response = "ERROR: Unsupported model"

        # Parse response
        is_appropriate = "CORRECT" in response.upper()
        determination = "CORRECT" if is_appropriate else "ERROR"

        # Extract confidence and justification
        confidence = "Medium"
        justification = response

        if "CONFIDENCE:" in response:
            parts = response.split("CONFIDENCE:")
            if len(parts) > 1:
                conf_line = parts[1].split("\n")[0].strip()
                confidence = conf_line

        if "JUSTIFICATION:" in response:
            parts = response.split("JUSTIFICATION:")
            if len(parts) > 1:
                justification = parts[1].strip()

        return {
            "is_appropriate": is_appropriate,
            "confidence": confidence,
            "justification": justification,
            "model_response": response,
            "determination": determination
        }

    def validate_scenario_images(
        self,
        clinical_images: list,
        prescribed_treatment: str,
        patient_context: Optional[Dict] = None,
        images_base_path: Optional[Path] = None
    ) -> list:
        """
        Validate all clinical images in a scenario

        Args:
            clinical_images: List of ClinicalImage objects
            prescribed_treatment: Prescribed treatment
            patient_context: Optional patient demographics
            images_base_path: Base path to clinical images directory

        Returns:
            List of validation results
        """
        results = []

        for clinical_image in clinical_images:
            # Construct full image path
            if images_base_path:
                image_path = images_base_path / clinical_image.file_path
            else:
                # Default to benchmarks directory
                image_path = Path(__file__).parent.parent.parent.parent / "benchmarks" / "clinical_images" / "kaggle_datasets" / "selected" / clinical_image.file_path

            # Validate
            if image_path.exists():
                validation = self.validate_treatment(
                    image_path,
                    clinical_image.finding,
                    prescribed_treatment,
                    patient_context
                )
                validation["modality"] = clinical_image.modality
                validation["image_file"] = clinical_image.file_path
                results.append(validation)
            else:
                results.append({
                    "is_appropriate": True,  # Skip validation if image not found
                    "confidence": "N/A",
                    "justification": f"Image not found: {image_path}",
                    "model_response": "Image file not available",
                    "determination": "SKIP",
                    "modality": clinical_image.modality,
                    "image_file": clinical_image.file_path
                })

        return results
