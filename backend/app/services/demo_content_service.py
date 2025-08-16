import random
from app.schemas.chat import ResponseContent, WorkflowType


class DemoContentService:
    
    @staticmethod
    def get_basic_response() -> ResponseContent:
        return ResponseContent(
            text="Based on your description of yellow leaves in wheat, this appears to be nitrogen deficiency. Apply 10-15 kg urea per acre during the next irrigation cycle. Mix with irrigation water for even distribution. Visible improvement expected in 7-10 days."
        )
    
    @staticmethod
    def get_disease_response() -> ResponseContent:
        return ResponseContent(
            text="The symptoms you describe indicate a possible fungal infection. Early treatment is crucial to prevent spread. Spray Mancozeb at 2.5g per liter of water and remove affected leaves immediately. Repeat treatment after 7 days.",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            video_title="How to Identify and Treat Crop Fungal Infections"
        )
    
    @staticmethod
    def get_scheme_response() -> ResponseContent:
        return ResponseContent(
            text="You may be eligible for PM-KISAN scheme which provides ₹6000 annual income support to farmers through direct benefit transfer of ₹2000 every 4 months. Required documents include Aadhaar and land records.",
            website_url="https://pmkisan.gov.in",
            website_title="PM-KISAN Official Portal - Apply Now"
        )
    
    @staticmethod
    def get_complex_response() -> ResponseContent:
        return ResponseContent(
            text="Based on the image analysis, your tomato crop shows signs of late blight disease. This requires immediate attention to prevent crop loss. Apply copper-based fungicide immediately and ensure proper drainage to reduce moisture. Consider crop insurance claim if damage exceeds 33%.",
            video_url="https://www.youtube.com/watch?v=abc123",
            video_title="Late Blight Management in Tomatoes",
            website_url="https://agricoop.nic.in/crop-insurance",
            website_title="Pradhan Mantri Fasal Bima Yojana - File Claim"
        )
    
    @classmethod
    def select_demo_response(cls, workflow_type: WorkflowType) -> ResponseContent:
        if workflow_type in [WorkflowType.AUDIO_ONLY, WorkflowType.TEXT_ONLY]:
            return random.choice([
                cls.get_basic_response(),
                cls.get_disease_response(),
                cls.get_scheme_response()
            ])
        elif workflow_type in [WorkflowType.AUDIO_WITH_IMAGE, WorkflowType.TEXT_WITH_IMAGE]:
            return random.choice([
                cls.get_disease_response(),
                cls.get_complex_response()
            ])
        else:
            return cls.get_basic_response()