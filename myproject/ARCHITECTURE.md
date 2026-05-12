# HoopTrack Action-Based Architecture

This project follows an action-partitioned architecture for clarity and maintainability.

## Core Rule

Every new file must be named by the exact action/functionality it implements.

Examples:

- `register_user_request.py`
- `register_user_controller.py`
- `register_user_service.py`
- `register_user_view.py`
- `register_user_page.html`
- `register_user_script.html`

Avoid generic names in partition folders such as `utils.py`, `misc.py`, or `common.py`.

## Layering

Request -> Controller -> Service -> Model access

- **Request**: parse/validate incoming payloads
- **Controller**: orchestration and use-case coordination
- **Service**: business logic and integrations
- **View**: transport layer (HTTP only), delegates to controllers
- **Template/Script**: page-specific rendering and interaction per action

## File Structure Convention

- `app/http/requests/<feature>/<action>_request.py`
- `app/controllers/<feature>/<action>_controller.py`
- `app/services/<feature>/<action>_service.py`
- `app/api/views/<feature>/<action>_view.py`
- `app/models/<feature>/<entity>_model.py`
- `templates/app/pages/<feature>/<action>_page.html`
- `templates/app/scripts/<feature>/<action>_script.html`
- `templates/app/partials/<feature>/<action>_partial.html`

## Naming Verbs

Use explicit verbs:

- `create`
- `update`
- `delete`
- `list`
- `generate`
- `sync`
- `request`
- `resolve`
- `render`

## Backward Compatibility Rule

When migrating existing flows:

1. Introduce action modules first.
2. Keep existing routes stable.
3. Use compatibility wrappers in legacy files temporarily.
4. Remove wrappers only after UI/API verification.
