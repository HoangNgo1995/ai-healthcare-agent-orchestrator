# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import base64
import logging
from io import BytesIO

from semantic_kernel.contents import ChatMessageContent, ImageContent, TextContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel import Kernel

from data_models.chat_context import ChatContext
from data_models.plugin_configuration import PluginConfiguration

logger = logging.getLogger(__name__)


def create_plugin(plugin_config: PluginConfiguration):
    """Create the Radiology Vision plugin for GPT-4o."""
    return RadiologyVisionPlugin(
        kernel=plugin_config.kernel,
        chat_ctx=plugin_config.chat_ctx,
        data_access=plugin_config.data_access,
    )


class RadiologyVisionPlugin:
    """Plugin for analyzing radiology images using GPT-4o Vision."""

    def __init__(self, kernel: Kernel, chat_ctx: ChatContext, data_access):
        self.kernel = kernel
        self.chat_ctx = chat_ctx
        self.data_access = data_access

    @kernel_function(
        description="Analyzes chest X-ray or CT scan images and generates radiology findings using GPT-4o Vision"
    )
    async def analyze_radiology_image(
        self, patient_id: str, filename: str, indication: str
    ) -> str:
        """
        Analyze a radiology image (chest X-ray or CT scan) using GPT-4o Vision.

        Args:
            patient_id (str): The ID of the patient
            filename (str): The name of the image file to analyze
            indication (str): The medical indication or reason for imaging (e.g., "Chest pain", "Pneumonia")

        Returns:
            str: Structured radiology findings from GPT-4o Vision
        """
        try:
            # Read the image from blob storage
            image_stream: BytesIO = await self.data_access.image_accessor.read(
                patient_id, filename
            )
            image_bytes = image_stream.getvalue()

            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            # Determine image type from filename
            image_type = self._determine_image_type(filename)

            # Create the prompt for GPT-4o Vision
            system_prompt = self._get_system_prompt(image_type)
            user_prompt = self._get_user_prompt(indication, image_type)

            # Create chat message with image
            messages = [
                ChatMessageContent(
                    role=AuthorRole.SYSTEM,
                    items=[TextContent(text=system_prompt)],
                ),
                ChatMessageContent(
                    role=AuthorRole.USER,
                    items=[
                        TextContent(text=user_prompt),
                        ImageContent(data=base64_image, data_format="base64"),
                    ],
                ),
            ]

            # Get the default chat completion service
            chat_service = self.kernel.get_service(service_id="default")

            # Invoke GPT-4o Vision
            response = await chat_service.get_chat_message_contents(
                chat_history=messages,
                settings=chat_service.get_prompt_execution_settings_class()(
                    temperature=0.3, max_tokens=2000
                ),
            )

            findings = str(response[0])

            logger.info(
                f"Successfully analyzed {image_type} image: {filename} for patient: {patient_id}"
            )

            return findings

        except Exception as e:
            logger.error(
                f"Error analyzing radiology image {filename} for patient {patient_id}: {str(e)}"
            )
            return f"Error analyzing image: {str(e)}"

    def _determine_image_type(self, filename: str) -> str:
        """Determine if image is X-ray or CT scan based on filename or metadata."""
        filename_lower = filename.lower()
        if "xray" in filename_lower or "x-ray" in filename_lower:
            return "chest X-ray"
        elif "ct" in filename_lower or "scan" in filename_lower:
            return "CT scan"
        else:
            # Default to X-ray if cannot determine
            return "chest X-ray"

    def _get_system_prompt(self, image_type: str) -> str:
        """Get the system prompt for GPT-4o Vision based on image type."""
        return f"""You are an expert radiologist analyzing {image_type} images.

Your task is to provide a detailed, structured radiology report following standard medical reporting format.

For chest X-rays, include:
- Technical Quality
- Comparison (if prior images mentioned)
- Findings:
  * Lungs (opacities, consolidations, nodules, masses)
  * Pleura (effusions, pneumothorax)
  * Heart and mediastinum (size, contours)
  * Bones and soft tissues
- Impression (summary of key findings)

For CT scans, include:
- Technical Quality
- Comparison (if prior images mentioned)
- Findings (organized by anatomical region):
  * Lungs and airways
  * Mediastinum and hila
  * Pleura
  * Heart and great vessels
  * Bones and soft tissues
  * Any masses, nodules, or abnormalities with size measurements
- Impression (summary of key findings with clinical significance)

Use clear, professional medical terminology. Be specific about locations, sizes, and characteristics of any abnormalities."""

    def _get_user_prompt(self, indication: str, image_type: str) -> str:
        """Get the user prompt for analysis."""
        return f"""Please analyze this {image_type} image.

Clinical Indication: {indication}

Provide a complete radiology report following the standard structured format. Include all relevant findings and measurements."""
