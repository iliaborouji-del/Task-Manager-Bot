from datetime import datetime, timedelta, timezone, date
import jdatetime

IRAN_TZ = timezone(timedelta(hours=3, minutes=30))


def now_iran() -> datetime:
    return datetime.now(IRAN_TZ)


def make_iran(dt: datetime) -> datetime:
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=IRAN_TZ)

    return dt.astimezone(IRAN_TZ)


def iran_to_naive(dt: datetime) -> datetime:
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt

    return dt.replace(tzinfo=None)


def naive_to_iran(dt: datetime) -> datetime:
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=IRAN_TZ)

    return dt.astimezone(IRAN_TZ)


def jalali_string(dt: datetime, fmt: str = "%Y/%m/%d  %H:%M") -> str:
    dt = naive_to_iran(dt)
    jalali = jdatetime.datetime.fromgregorian(datetime=dt)
    return jalali.strftime(fmt)


def jalali_to_gregorian(year: int, month: int, day: int, hour: int, minute: int) -> datetime:
    jdt = jdatetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute
    )

    gdt = jdt.togregorian()

    return gdt.replace(tzinfo=IRAN_TZ)


def is_past(dt: datetime) -> bool:
    return make_iran(dt) <= now_iran()

def jalali_date_string(dt: date, fmt: str = "%Y/%m/%d") -> str:
    if dt is None:
        return "_"

    return jdatetime.date.fromgregorian(date=dt).strftime(fmt)