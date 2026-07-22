from sqlalchemy import select
from datetime import timedelta, datetime
from collections import Counter
from bot.database.models import Tasks
from bot.utils.datetime import (
    now_iran,
    iran_to_naive,
)

#----- get_date_range -----
def get_date_range(report_type: str):
    now = now_iran()
    
    if report_type == "weekly":
        start = now - timedelta(days=7)
    elif report_type == "monthly":
        start = now - timedelta(days=30)
    elif report_type == "yearly":
        start = now - timedelta(days=365)
    else:
        raise ValueError("نوع گزارش نامعتبر است.")
    
    return start, now

#----- total tasks -----
async def get_total_tasks(session, user_id: int, start: datetime, end: datetime):
    result = await session.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.created_at.between(start, end)
        )
    )
    return result.scalars().all()

#----- completed tasks -----
async def get_completed_tasks(session, user_id: int, start: datetime, end: datetime):
    result = await session.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.status == "انجام شده ✅",
            Tasks.created_at.between(start, end)
        )
    )
    return result.scalars().all()

#----- in progress tasks -----
async def get_in_progress_tasks(session, user_id: int, start: datetime, end: datetime):
    result = await session.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.status == "در حال انجام ⏳",
            Tasks.created_at.between(start, end)
        )
    )
    return result.scalars().all()

#----- not done tasks -----
async def get_not_done_tasks(session, user_id: int, start: datetime, end: datetime):
    result = await session.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.status == "انجام نشده ⭕",
            Tasks.created_at.between(start, end)
        )
    )
    return result.scalars().all()

#----- overdue tasks -----
async def get_overdue_tasks(session, user_id: int, start: datetime, end: datetime):
    now = iran_to_naive(now_iran())
    
    result = await session.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.status != "انجام شده ✅",
            Tasks.created_at.between(start, end)
        )
    )
    tasks = result.scalars().all()
    overdue = []
    for task in tasks:
        try:
            deadline_dt = task.deadline
            if deadline_dt < now:
                overdue.append(task)
        except Exception:
            continue
    return overdue

#----- completion_rate -----
def calc_completion_rate(total: int, completed: int):
    if total == 0:
        return 0
    return round((completed / total) * 100)

#----- on time -----
def calc_on_time(completed_tasks):
    if not completed_tasks:
        return 0
    on_time_count = 0
    counted = 0
    for task in completed_tasks:
        try:
            if not task.completed_at:
                continue
            counted += 1

            deadline_dt = task.deadline
            
            if task.completed_at <= deadline_dt:
                on_time_count += 1
        except Exception:
            continue
    if counted == 0:
        return 0
    return round((on_time_count / counted) * 100)
            

#----- get_most_active_day -----
async def get_most_active_days(session, user_id: int, start: datetime, end: datetime):
    result = await session.execute(
        select(Tasks.created_at).where(
            Tasks.user_id == user_id,
            Tasks.created_at.between(start, end)
        )
    )
    
    dates = [t.date() for t in result.scalars().all()]
    
    if not dates:
        return None, 0
    
    counter = Counter(dates)
    day, count = counter.most_common(1)[0]
    
    return day, count

#----- idle days -----
def get_idle_days(start: datetime, end: datetime, active_dates: list):
    idle = 0
    current = start.date()
    
    while current <= end.date():
        if current not in active_dates:
            idle += 1
        current += timedelta(days=1)
        
    return idle

#----- next deadline -----
async def get_next_deadline(session, user_id: int):
    now = iran_to_naive(now_iran())
    result = await session.execute(
        select(Tasks).where(Tasks.user_id == user_id)
    )
    tasks = result.scalars().all()
    nearest = None

    for task in tasks:
        if task.status == "انجام شده ✅":
            continue
        if task.deadline is None:
            continue

        deadline_dt = task.deadline

        if deadline_dt > now:
            if nearest is None or deadline_dt < nearest[0]:
                nearest = (deadline_dt, task)

    return nearest[1] if nearest else None