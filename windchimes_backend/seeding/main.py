import argparse
import asyncio
import json
import random

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from windchimes_backend.api_clients.soundcloud import SoundcloudApiClient
from windchimes_backend.core.database import database
from windchimes_backend.core.database.models.playlist import Playlist
from windchimes_backend.core.database.models.track_reference import TrackReference
from windchimes_backend.core.database.models import database_models
from windchimes_backend.core.models.track import TrackReferenceSchema
from windchimes_backend.core.regular_tasks.soundcloud_client_id_obtaining import (
    obtain_soundcloud_client_id,
)
from windchimes_backend.core.stores.soundcloud_api_client_id_store import (
    get_soundcloud_api_client_id,
)

FAKE_USERS_IDS = ["auth0|670260d16db103f2c052c4a6", "auth0|67026116a3270625dab1d482"]
DATA_FILES_PATH = "./windchimes_backend/seeding/data"


parser = argparse.ArgumentParser(prog="WindchimesDatabaseSeeding")
parser.add_argument(
    "-r",
    "--reset",
    help="drop all tables and create new ones",
    default=False,
    action="store_true",
)


async def add_playlists(database_session: AsyncSession):
    with (
        open(
            f"{DATA_FILES_PATH}/soundcloud-tracks.json", "rt", encoding="utf-8"
        ) as soundcloud_tracks_stream,
        open(
            f"{DATA_FILES_PATH}/youtube-videos.json", "rt", encoding="utf-8"
        ) as youtube_videos_stream,
    ):
        track_references_dicts = [
            *json.loads(soundcloud_tracks_stream.read()),
            *json.loads(youtube_videos_stream.read()),
        ]

        track_references = [
            TrackReferenceSchema(**track_reference_dict)
            for track_reference_dict in track_references_dicts
        ]

    await obtain_soundcloud_client_id()
    soundcloud_api_client = SoundcloudApiClient(get_soundcloud_api_client_id())

    playlists = await soundcloud_api_client.search_playlists("jazz")

    database_track_references = [
        TrackReference(
            id=track.id,
            platform_id=track.platform_id,
            platform=track.platform,
        )
        for track in track_references
    ]

    playlists_to_add_to_database = [
        Playlist(
            name=playlist.title,
            description=playlist.description,
            picture_url=(
                playlist.artwork_url.replace("-large.jpg", "-t500x500.jpg")
                if playlist.artwork_url is not None
                else None
            ),
            owner_user_id=random.choice(FAKE_USERS_IDS),
            track_references=random.sample(
                database_track_references, k=random.randint(200, 300)
            ),
        )
        for playlist in playlists
    ]

    database_session.add_all(playlists_to_add_to_database)
    await database_session.commit()


async def start_seeding():
    try:
        async with database.create_session() as database_session:
            args = parser.parse_args()

            if args.reset:
                print("Deleting all records from the tables")
                for model in database_models:
                    await database_session.execute(
                        text(f"DELETE FROM {model.__tablename__}")
                    )

                await database_session.commit()

            await add_playlists(database_session)
    except Exception as error:
        print(error)

    await database.close()


asyncio.run(start_seeding())
