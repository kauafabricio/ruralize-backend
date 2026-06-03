from fastapi import HTTPException
from app.repositories.event_repository import EventRepository
from app.repositories.action_repository import ActionRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.event_schema import EventCreate, EventUpdate


class EventService:

    def __init__(self, event_repo: EventRepository, action_repo: ActionRepository = None, profile_repo: ProfileRepository = None):
        self.event_repo = event_repo
        self.action_repo = action_repo
        self.profile_repo = profile_repo

    def _enrich_event(self, event):
        """Enrich event with promoter and action data"""
        if not event:
            return event

        enriched = event.copy()

        if self.profile_repo:
            promoter = self.profile_repo.find_by_user_id(event["promoter_id"])
            enriched["promoter_name"] = promoter.get("name", "Desconhecido") if promoter else "Desconhecido"
            enriched["promoter_photo"] = promoter.get("profile_photo_url") if promoter else None

        if self.action_repo:
            action = self.action_repo.get_action_by_id(event["action_id"])
            enriched["action_name"] = action.get("name", "Desconhecida") if action else "Desconhecida"

        return enriched

    def _validate_dates(self, start_date, end_date):
        """Validate that start_date is before end_date"""
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="Data de início deve ser antes da data de fim")

    def _validate_points(self, points):
        """Validate that points is positive"""
        if points <= 0:
            raise HTTPException(status_code=400, detail="Pontos devem ser maiores que zero")

    def _validate_participants(self, max_participants):
        """Validate that max_participants is positive"""
        if max_participants <= 0:
            raise HTTPException(status_code=400, detail="Máximo de participantes deve ser maior que zero")

    def get_all_events(self):
        events = self.event_repo.get_all_events()
        return [self._enrich_event(e) for e in events]

    def get_event(self, event_id: str):
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")
        return self._enrich_event(event)

    def get_events_by_filter(self, action_id: str = None, status: str = None, start_date = None, end_date = None):
        filters = {}
        if action_id:
            filters["action_id"] = action_id
        if status:
            filters["status"] = status
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date

        events = self.event_repo.get_events_by_filter(filters)
        return [self._enrich_event(e) for e in events]

    def create_event(self, event_data: EventCreate, current_user: dict):
        # Only teachers can create events
        if current_user.get("role") != "teacher":
            raise HTTPException(status_code=403, detail="Apenas professores podem criar eventos")

        # Validate dates
        self._validate_dates(event_data.start_date, event_data.end_date)

        # Validate points
        self._validate_points(event_data.points)

        # Validate max participants
        self._validate_participants(event_data.max_participants)

        payload = event_data.dict()
        payload["promoter_id"] = current_user["id"]

        event_id = self.event_repo.create_event(payload)
        return {"message": "Evento criado com sucesso", "id": event_id}

    def update_event(self, event_id: str, event_data: EventUpdate, current_user: dict):
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")

        # Only promoter can edit
        if event["promoter_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Você não tem permissão para editar este evento")

        update_payload = {k: v for k, v in event_data.dict().items() if v is not None}

        # Validate dates if updating
        if update_payload.get("start_date") or update_payload.get("end_date"):
            start = update_payload.get("start_date") or event["start_date"]
            end = update_payload.get("end_date") or event["end_date"]
            self._validate_dates(start, end)

        # Validate points if updating
        if update_payload.get("points"):
            self._validate_points(update_payload["points"])

        # Validate max participants if updating
        if update_payload.get("max_participants"):
            self._validate_participants(update_payload["max_participants"])

        result = self.event_repo.update_event(event_id, update_payload)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Evento não encontrado")

        return {"message": "Evento atualizado com sucesso"}

    def delete_event(self, event_id: str, current_user: dict):
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento não encontrado")

        # Only promoter can delete
        if event["promoter_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Você não tem permissão para deletar este evento")

        result = self.event_repo.delete_event(event_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Evento não encontrado")

        return {"message": "Evento deletado com sucesso"}

    def register_user(self, event_id: str, current_user: dict):
    event = self.event_repo.get_event_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Evento não encontrado"
        )

    if event["participant_count"] >= event["max_participants"]:
        raise HTTPException(
            status_code=400,
            detail="Evento lotado"
        )

    result = self.event_repo.register_user(
        event_id,
        current_user["id"]
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Usuário já inscrito"
        )

    return {
        "message": "Inscrição realizada com sucesso"
    }


def unregister_user(self, event_id: str, current_user: dict):
    self.event_repo.unregister_user(
        event_id,
        current_user["id"]
    )

    return {
        "message": "Inscrição cancelada com sucesso"
    }


def get_my_events(self, current_user: dict):
    events = self.event_repo.get_events_by_participant(
        current_user["id"]
    )

    return [self._enrich_event(e) for e in events]
