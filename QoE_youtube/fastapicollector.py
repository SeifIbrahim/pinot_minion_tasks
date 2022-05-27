import os
from typing import TextIO

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DUMP_FOLDER = "."
file_descriptors = {}


def create_file_ds(view_id: str) -> TextIO:
    global file_descriptors
    file = open(f"{os.path.join(DUMP_FOLDER, view_id)}.txt", "a")
    file_descriptors[view_id] = file
    return file


def parse_descriptor(text: str) -> str:
    return text.replace(r' / ', '_').replace(" ", "_")


def save_record(obj: dict, code="report") -> None:
    global file_descriptors
    if 'video_id_and_cpn' in obj:
        parsed_desc = parse_descriptor(obj['video_id_and_cpn'])
        name = f"{code}_{parsed_desc}"
        event_file = file_descriptors.get(name, create_file_ds(name))
        print(obj, file=event_file, flush=True)


@app.post("/quality")
async def quality(obj: dict) -> None:
    """
    On quality change
    :param obj:
    :return:
    """
    save_record(obj, "event")


@app.post("/state")
async def state(obj: dict) -> None:
    """
    On player state change
    :param obj:
    :return:
    """
    save_record(obj, "event")


@app.post("/report")
async def report(obj: dict) -> None:
    """
    Each Nms report
    :param obj:
    :return:
    """
    save_record(obj, "report")


@app.post("/meta")
async def meta(obj: dict) -> None:
    """
    One-time meta information report
    :param obj:
    :return:
    """
    save_record(obj, "meta")


def run(dump_folder: str = ".", host: str = "0.0.0.0", port: int = 34543):
    global app, DUMP_FOLDER
    DUMP_FOLDER = dump_folder
    try:
        uvicorn.run(app, host=host, port=port)
    except (KeyboardInterrupt, Exception) as e:
        for file in file_descriptors.values():
            file.close()
        raise


if __name__ == '__main__':
    run()
