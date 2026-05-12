from app.services.basketball_service import BasketballService


def bracket_update_action_service(instance, payload):
    normalized = BasketballService.normalize_bracket_payload(payload)
    for key, value in normalized.items():
        if value is not None:
            setattr(instance, key, value)
    instance.save()
    BasketballService.replace_bracket_relations(
        instance,
        matchups=payload.get("matchups"),
        standings=payload.get("standings"),
    )
    return instance
