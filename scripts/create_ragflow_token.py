from datetime import datetime

from api.db.services.api_service import APITokenService
from api.db.services.user_service import UserService, UserTenantService
from api.utils.api_utils import generate_confirmation_token
from common.time_utils import current_timestamp, datetime_format

EMAIL = "admin@local.ragflow"
SOURCE = "hermes"

users = UserService.query(email=EMAIL)
if not users:
    raise SystemExit(f"User not found: {EMAIL}")

tenants = UserTenantService.query(user_id=users[0].id)
tenant_id = [tenant for tenant in tenants if tenant.role == "owner"][0].tenant_id

for item in APITokenService.query(tenant_id=tenant_id):
    if item.source == SOURCE:
        print(item.token)
        raise SystemExit(0)

obj = {
    "tenant_id": tenant_id,
    "token": generate_confirmation_token(),
    "beta": generate_confirmation_token().replace("ragflow-", "")[:32],
    "dialog_id": None,
    "source": SOURCE,
    "create_time": current_timestamp(),
    "create_date": datetime_format(datetime.now()),
    "update_time": None,
    "update_date": None,
}

APITokenService.save(**obj)
print(obj["token"])
