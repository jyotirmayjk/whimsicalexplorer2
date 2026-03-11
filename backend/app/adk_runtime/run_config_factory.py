from app.models.db_models import Session, HouseholdSettings
from app.models.enums import AppMode, VoiceStyle

class RunConfigFactory:
    """
    Derives the Google Gemini Live API RunConfig dynamically based on 
    the Kids Pokedex active session configuration and household safety rules.
    """
    @staticmethod
    def build_config(session: Session, settings: HouseholdSettings) -> dict:
        
        # Base System Prompt ensuring Toddler safety and Object centricity
        system_instruction = (
            "You are a magical, friendly, and calm AI companion for a 2-4 year old child. "
            "You MUST keep your responses short, warm, positive, and non-judgmental. "
            "Never use violence, fear-inducing content, or adult topics. "
            "Do not instruct the child to do dangerous things. "
            "We are focusing on exploring objects together."
        )
        
        # Inject Context 
        if session.current_object_name:
            system_instruction += f"\n\nThe child is currently looking at a {session.current_object_name} ({session.current_object_category}). "
        else:
             system_instruction += "\n\nThe child has not scanned an object yet. Encourage them to point the camera at a toy or animal."

        # Apply Mode Policy
        if session.active_mode == AppMode.story:
             system_instruction += (
                 f"\n\nSTORY MODE: You must create and narrate a short, magical, and imaginative "
                 f"2-sentence story involving the {session.current_object_name}. "
             )
        elif session.active_mode == AppMode.learn:
             system_instruction += (
                 f"\n\nIDENTIFICATION MODE: You must first slowly and clearly enunciate the word '{session.current_object_name}'. "
                 f"Then, create a very short, simple 1-sentence rhyme about it. "
                 f"Finally, tell the child exactly 1 easy-to-understand educational fact about it."
             )
        elif session.active_mode == AppMode.explorer:
             system_instruction += " Ask the child a playful, highly-engaging question about the object's color or sound."

        # Apply Voice Policy (Mapping to Google TTS or Gemini Voice aliases)
        voice_name = "Aoede" if session.voice_style == VoiceStyle.story_narrator else "Puck"

        return {
            "model": "models/gemini-2.0-flash-exp",
            "generation_config": {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                         "prebuilt_voice_config": {
                              "voice_name": voice_name
                         }
                    }
                }
            },
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            }
        }
