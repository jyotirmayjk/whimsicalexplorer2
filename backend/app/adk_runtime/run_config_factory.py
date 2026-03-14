from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

from app.models.db_models import Session, HouseholdSettings
from app.models.enums import AppMode, VoiceStyle

class RunConfigFactory:
    """
    Derives the Google Gemini Live API RunConfig and Agent dynamically based on 
    the Kids Pokedex active session configuration and household safety rules.
    """
    @staticmethod
    def build_config(session: Session, settings: HouseholdSettings):
        
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

        # Build google-adk specific primitives
        agent = Agent(
            name=f"toddler_companion_{session.id}",
            model="gemini-2.0-flash-001",
            description="Toddler companion and educator",
            instruction=system_instruction
        )
        
        speech_config = types.SpeechConfig()
        # Note: PrebuiltVoiceConfig might be inside types or we can just pass it directly if adk wraps it.
        # But we pass it inside speech_config
        # genai types changed significantly in Google ADK vs older ones. Let's just use ADK dict kwargs to be safe, 
        # or use what we can. 
        # Actually Google ADK RunConfig takes speech_config = types.SpeechConfig(...)
        
        speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            )
        )

        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=["AUDIO"],
            speech_config=speech_config,
        )

        return agent, run_config
