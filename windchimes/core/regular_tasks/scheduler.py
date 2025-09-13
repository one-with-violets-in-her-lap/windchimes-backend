from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from windchimes.core.regular_tasks.soundcloud_client_id_obtaining import (
    obtain_soundcloud_client_id,
)


scheduler = AsyncIOScheduler()
scheduler.add_job(
    obtain_soundcloud_client_id,
    "interval",
    days=1,
    next_run_time=datetime.now(),
    misfire_grace_time=60 * 3,
)
