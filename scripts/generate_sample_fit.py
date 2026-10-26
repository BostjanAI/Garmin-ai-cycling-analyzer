"""Ustvari majhno, veljavno kolesarsko FIT aktivnost za lokalni preizkus."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def generate(output: Path) -> Path:
    try:
        from garmin_fit_sdk import Encoder, FIT_EPOCH_S, Profile
    except ImportError as error:
        raise SystemExit(
            "Manjka uradni Garmin SDK. Najprej zaženite: pip install -e ."
        ) from error

    output.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 10, 18, 8, 0, tzinfo=UTC)
    start_fit = int(start.timestamp()) - FIT_EPOCH_S
    encoder = Encoder()

    encoder.write_mesg(
        {
            "mesg_num": Profile["mesg_num"]["FILE_ID"],
            "type": "activity",
            "manufacturer": "development",
            "product": 1,
            "serial_number": 530001,
            "time_created": start_fit,
        },
    )
    encoder.write_mesg(
        {
            "mesg_num": Profile["mesg_num"]["EVENT"],
            "timestamp": start_fit,
            "event": "timer",
            "event_type": "start",
        }
    )

    # Tridesetsekundni zapisi so dovolj gosti tudi za izračun časa v območjih.
    samples = 121
    step_seconds = 30
    for index in range(samples):
        timestamp = start_fit + index * step_seconds
        encoder.write_mesg(
            {
                "mesg_num": Profile["mesg_num"]["RECORD"],
                "timestamp": timestamp,
                "distance": index * 250.0,
                "enhanced_speed": 8.0 + index * 0.005,
                "heart_rate": 118 + min(index // 10, 36),
                "cadence": 78 + index % 6,
                "power": 155 + min(index // 4, 60),
                "enhanced_altitude": 300.0 + (index % 4) * 12.0,
            },
        )

    end_fit = start_fit + (samples - 1) * step_seconds
    encoder.write_mesg(
        {
            "mesg_num": Profile["mesg_num"]["EVENT"],
            "timestamp": end_fit,
            "event": "timer",
            "event_type": "stop",
        }
    )
    summary = {
        "timestamp": end_fit,
        "start_time": start_fit,
        "total_elapsed_time": 3600.0,
        "total_timer_time": 3600.0,
        "total_distance": 30000.0,
        "sport": "cycling",
        "sub_sport": "road",
        "avg_heart_rate": 136,
        "max_heart_rate": 154,
        "avg_cadence": 80,
        "total_ascent": 144,
        "avg_power": 185,
        "max_power": 215,
    }
    encoder.write_mesg(
        {**summary, "mesg_num": Profile["mesg_num"]["LAP"], "message_index": 0}
    )
    encoder.write_mesg(
        {
            **summary,
            "mesg_num": Profile["mesg_num"]["SESSION"],
            "message_index": 0,
            "first_lap_index": 0,
            "num_laps": 1,
        }
    )
    encoder.write_mesg(
        {
            "mesg_num": Profile["mesg_num"]["ACTIVITY"],
            "timestamp": end_fit,
            "total_timer_time": 3600.0,
            "num_sessions": 1,
            "local_timestamp": end_fit,
        },
    )

    output.write_bytes(bytes(encoder.close()))
    return output


def main() -> None:
    output = generate(Path("fit_inbox/sample_ride.fit"))
    print(f"Ustvarjeno: {output}")


if __name__ == "__main__":
    main()

