from sqlalchemy.orm import Session
from app.models.db_models import Discovery, Session as DBSession, ActivityEvent
from app.models.enums import ObjectCategory

class PersistenceService:
    @staticmethod
    def create_discovery(db: Session, session: DBSession) -> Discovery | None:
        """
        Derives a new Discovery securely from the current Session context
        Only creates one if an active image context & valid category exists.
        """
        if not session.current_image_context_id or not session.current_object_name:
            return None
            
        # Optional constraint check: ensure not already discovered recently
        existing = db.query(Discovery).filter(
            Discovery.session_id == session.id,
            Discovery.name == session.current_object_name
        ).first()
        
        if existing:
            return existing

        new_discovery = Discovery(
            session_id=session.id,
            image_context_id=session.current_image_context_id,
            name=session.current_object_name,
            category=session.current_object_category
        )
        
        db.add(new_discovery)
        
        # Log mapping event
        event = ActivityEvent(
            session_id=session.id,
            event_type="discovery_created",
            metadata_json={"object_name": new_discovery.name, "category": new_discovery.category.value}
        )
        db.add(event)
        
        db.commit()
        db.refresh(new_discovery)
        return new_discovery
        
    @staticmethod
    def log_activity(db: Session, session_id: int, event_type: str, metadata: dict = None):
         event = ActivityEvent(
             session_id=session_id,
             event_type=event_type,
             metadata_json=metadata or {}
         )
         db.add(event)
         db.commit()
