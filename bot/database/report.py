from sqlalchemy import select
from datetime import datetime, timedelta
from collections import Counter
from bot.database.models import Tasks

#----- get_date_range -----
def get_date_range(report_type: str):
    now = datetime.utcnow()
    
    if report_type == "weeklt":
        start = now - timedelta(days=7)
        
    elif report_type == "monthly":
        start = now - timedelta(days=30)
        
    elif report_type == "yearly":
        start = now - timedelta(days=365)
        
    else:
        raise ValueError("نوع گزارش نامعتبر است.")
    
    return start, now

#----- total tasks -----
async def get_total_tasks(session, user_id, start: datetime, end: datetime):
    result = await session.execute(select(Tasks).where(
        Tasks.user_id == user_id,
        Tasks.created_at.between(start, end)
    ))
    return result.scalars().all()

#----- completed tasks -----
async def get_completed_tasks(session, user_id, start: datetime, end: datetime):
    result = await session.execute(select(Tasks).where(
        Tasks.user_id == user_id,
        Tasks.status == "انجام شده✅",
        Tasks.created_at.between(start, end)
    ))
    return result.scalars().all()

#----- in progress tasks -----
async def get_in_progress_tasks(session, user_id, start: datetime, end: datetime):
    result = await session.execute(select(Tasks).where(
        Tasks.user_id == user_id,
        Tasks.status == "در حال انجام⏳",
        Tasks.created_at.between(start, end)
    ))
    return result.scalars().all()

#----- not done tasks -----
async def get_not_done_tasks(session, user_id, start: datetime, end: datetime):
    result = await session.execute(select(Tasks).where(
        Tasks.user_id == user_id,
        Tasks.status == "انجام نشده⭕",
        Tasks.created_at.between(start, end)
    ))
    return result.scalars().all()

#----- overdue tasks -----
async def get_overdue_tasks(session, user_id, start: datetime, end: datetime):
    now = datetime.utcnow()
    
    result = await session.execute(select(Tasks).where(
        Tasks.user_id == user_id,
        Tasks.status != "انجام شده✅",
        Tasks.deadline < now,
        Tasks.created_at.between(start, end)
    ))
    return result.scalars().all()

#----- completion_rate -----
async def calc_completion_rate(total: int, completed: int):
    if total == 0:
        return 0
    return round((completed / total) * 100)

#----- on time -----
async def calc_on_time(completed_tasks):
    if not completed_tasks:
        return 0
    
    on_time = sum(1 for t in completed_tasks if t.completed_at and t.completed_at <= t.deadline)
    return round((on_time / len(completed_tasks)) * 100)

#----- get_most_active_day -----
async def get_most_active_days(session, user_id, start: datetime, end: datetime):
    result = await session.execute(select(Tasks.created_at).where(
        Tasks.user_id == user_id,
        Tasks.created_at.between(start, end)
    ))
    
    dates = [t.date() for t in result.scalars().all()]
    
    if not dates:
        return None, 0
    
    counter = Counter()
    day, count = counter.most_common(1)[0]
    
    return day, count

#----- idle days -----
async def get_idle_days(start: datetime, end: datetime, active_dates):
    all_days = set(start.date() + timedelta(days=i) for i in range((end - start).days + 1))
    return len(all_days - set(active_dates))

#----- next deadline -----
async def get_next_deadline(session, user_id):
    now = datetime.utcnow()
    
    result = await session.execute(select(Tasks).where(
        Tasks.user_id == user_id,
        Tasks.deadline > now
    ).order_by(Tasks.deadline.asc()))
    
    return result.scalars().all()