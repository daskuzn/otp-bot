import datetime as dt
from datetime import timezone
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from babel.dates import format_date
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.partner import admin_partners_kb
from middlewares.admin import AdminMiddleware
from models import User, Visit, Report, Task, Partner
from models.enums import Marketing, TaskType, UserRole
from keyboards.report import admin_reports_kb, delete_msg_kb, confirm_report_kb
from keyboards.tasks import admin_tasks_kb, partners_kb, reps_kb, task_types_kb, confirm_kb
from models.enums import TaskStatus

router = Router()

# Регистрация middleware для администраторов
# Это позволит использовать middleware для всех сообщений и callback-запросов в этом роутере
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())


@router.callback_query(F.data == "delete")
async def delete_message(call: CallbackQuery):
    await call.message.delete()


@router.callback_query(F.data == "admin_reps")
async def show_reps(call: CallbackQuery, session: AsyncSession):
    temp_msg = await call.message.answer("Загрузка репортёров...")
    result = await session.execute(
        select(User).where(User.role == UserRole.REP)
    )
    representors = result.scalars().all()
    if not representors:
        await call.message.answer("Нет репортёров.")
        return
    # Формируем список репортёров
    reps_list = ""
    cur_date = dt.datetime.now()
    month_name_ru = format_date(cur_date, "LLLL", locale="ru", ).capitalize()
    i = 1
    for rep in representors:
        visits_q = (
            select(func.count())
            .select_from(Visit)
            .where(
                Visit.rep_id == rep.id,   # ← фильтр по telegram_id
                Visit.visited_at >= cur_date,
            )
        )
        
        Visits_cnt: int = await session.scalar(visits_q)
        reps_list += (f"{i}. {rep.last_name} {rep.first_name} (ID: {rep.id}), {Visits_cnt} визитов за {month_name_ru}\n")
        i += 1
    await temp_msg.delete()
    await call.message.answer(f"Список репортёров:\n{reps_list}", reply_markup=delete_msg_kb())


@router.callback_query(F.data == "admin_reports")
async def show_reports(call: CallbackQuery, session: AsyncSession):
    temp_msg = await call.message.answer("Загрузка отчётов...")
    stmt = (
        select(Visit, Report, Task, Partner)
        .join(Visit.report)         # SQLAlchemy сам подставит ON Visit.report_id == Report.id
        .join(Report.task)          # ON Report.task_id == Task.id
        .join(Task.partner)       # ON Task.partner_id == Partner.id
        .where(Visit.visited_at.is_not(None))
        .order_by(Visit.visited_at.desc())
    )
    rows = (await session.execute(stmt)).all()
    if not rows:
        await call.message.answer("Нет отчётов.")
        return
    
    reports_str = ""
    i = 1
    reports_list: list[Report] = []
    for row in rows:
        visit: Visit = row[0]
        report: Report = row[1]
        reports_list.append(report)
        task: Task = row[2]
        partner: Partner = row[3]
        confirmed = ""
        if visit.notes == "Отчёт подтверждён администратором.":
            confirmed = "(Подтверждён)"
        elif visit.notes == "Отчёт отменён администратором.":
            confirmed = "(Отчёт отклонён)"
        else:
            confirmed = "(Не подтверждён)"
        reports_str += (
            f"{i}. ID отчёта: {report.id}, тип задания: {task.task_type}," 
            f"точка: {partner.name}, адрес: {partner.address} {confirmed}\n"
        )
        i += 1
    
    await temp_msg.delete()
    await call.message.answer(f"Список отчётов:\n{reports_str}\n\n"
                              f"Выберите отчёт для просмотра или удаления",
                              reply_markup=await admin_reports_kb(reports_list))
    

@router.callback_query(F.data.startswith("report_"))
async def show_report_details(call: CallbackQuery, session: AsyncSession):
    report_id = int(call.data.split("_")[1])
    stmt = (
        select(Visit, Report, Task, Partner)
        .join(Visit.report)         # SQLAlchemy сам подставит ON Visit.report_id == Report.id
        .join(Report.task)          # ON Report.task_id == Task.id
        .join(Task.partner)       # ON Task.partner_id == Partner.id
        .where(Visit.visited_at.is_not(None), Report.id == report_id)
    )
    row = (await session.execute(stmt)).first()
    
    if not row:
        await call.message.answer("Отчёт не найден.")
        return
    
    visit: Visit = row[0]
    report: Report = row[1]
    task: Task = row[2]
    partner: Partner = row[3]
    
    details = (
        f"ID отчёта: {report.id}\n"
        f"Тип задания: {task.task_type}\n"
        f"Партнёр: {partner.name}\n"
        f"Адрес: {partner.address}\n"
        f"Контактное лицо: {partner.contact_name}\n"
        f"Телефон: {partner.contact_phone}\n"
        f"Дата визита: {visit.visited_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"Информация о визите:\n"
        "<pre>"
        f"Есть ли рекламные материалы: {report.marketing}\n"
        f"Как часто клиенты оформляют кредит через ОТП: {report.interview}\n"
        f"Сколько клиентов оформили кредит в этом месяце: {report.share}\n"
        f"Банки-конкуренты: {report.competitors}\n"
        f"Комментарий: {report.comment}\n"
        "</pre>"
        "Все ли действия выполнены?"
    )
    photos: list[str] = report.photos_list.split(",") if len(report.photos_list) > 1 else report.photos_list
    visit_id = visit.id
    if len(photos) == 1:
        # одно фото → send_photo / answer_photo
        await call.message.answer_photo(
            photo=photos[0],
            caption=details,
            parse_mode="HTML",
            reply_markup=confirm_report_kb(visit_id)
        )
    else:
        # 2 и более фото → альбом
        media = [
            InputMediaPhoto(
                media=photos[0],
                caption=details,
                parse_mode="HTML",
            )
        ]
        # добавляем оставшиеся фото без подписи
        for file_id in photos[1:]:
            media.append(InputMediaPhoto(media=file_id))

        await call.message.answer_media_group(media)
        # после альбома можно отправить кнопки отдельным сообщением
        await call.message.answer(
            "Выберите действие с отчётом:",
            reply_markup=confirm_report_kb(visit_id)
        )


@router.callback_query(F.data.startswith("confirm_"))
async def confirm_report(call: CallbackQuery, session: AsyncSession):
    visit_id = int(call.data.split(":")[1])
    stmt = select(Visit).where(Visit.id == visit_id)
    visit = (await session.execute(stmt)).scalar_one_or_none()
    # Получаем связанный отчёт и задачу, чтобы обновить статус
    report = await session.get(Report, visit.report_id)
    task = await session.get(Task, report.task_id)

    if visit:
        if call.data.startswith("confirm_yes"):
            task.status = TaskStatus.DONE
            visit.marketing_checked = True
            visit.satisfaction_done = True
            visit.competitor_logged = True
            visit.notes = "Отчёт подтверждён администратором."
            await call.message.answer("Отчёт подтверждён.", reply_markup=delete_msg_kb())
        else:
            task.status = TaskStatus.CANCELED
            visit.marketing_checked = False
            visit.satisfaction_done = False
            visit.competitor_logged = False
            visit.notes = "Отчёт отменён администратором."
            await call.message.answer("Отчёт отменён.", reply_markup=delete_msg_kb())

        task.updated_at = dt.datetime.now(timezone.utc).replace(tzinfo=None)

        await session.commit()
    else:
        await call.message.answer("Отчёт не найден.", reply_markup=delete_msg_kb())


@router.callback_query(F.data == "admin_analytics")
async def show_analytics(call: CallbackQuery, session: AsyncSession):
    temp_msg = await call.message.answer("Загрузка аналитики...")
    # Получаем количество визитов за текущий месяц
    now = dt.datetime.now(dt.timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    visits_q = (
        select(func.count())
        .select_from(Visit)
        .where(Visit.visited_at >= month_start)
    )
    visits_cnt: int = await session.scalar(visits_q)
    # Получаем кол-во кредитов за текущий месяц
    credits_q = (
        select(func.sum(Report.share))
        .select_from(Report)
        .join(Visit, Visit.report_id == Report.id)
        .where(Visit.visited_at >= month_start)
    )
    credits_cnt: int = await session.scalar(credits_q)

    # Получаем наиболее частый ответ на вопрос "Как часто клиенты оформляют кредит через ОТП?"
    freq_q = (
        select(Report.interview, func.count().label("cnt"))
        .select_from(Report)
        .join(Visit, Visit.report_id == Report.id)
        .where(Visit.visited_at >= month_start)
        .group_by(Report.interview)
        .order_by(func.count().desc())
        .limit(1)
    )

    # Получаем процент рекламных материалов: Да=1, Частично=0.5, Нет=0
    mkt_q = (
        select(
            (func.sum(
                case(
                (Report.marketing == Marketing.YES,     1.0),
                (Report.marketing == Marketing.PARTIAL, 0.5),
                else_=0.0,
            )
            ) / func.count() * 100).label("mkt_percent")
        )
        .select_from(Report)
        .join(Visit, Visit.report_id == Report.id)
        .where(Visit.visited_at >= month_start)
    )
    marketing_percent = (await session.execute(mkt_q)).scalar_one() or 0

    # Получить 5 самых активных репортёров по количеству завершённых задач
    top_reps_q = (
        select(User.id, User.last_name, User.first_name, func.count(Task.id).label("cnt"))
        .join(Task, Task.rep_id == User.id)
        .where(Task.status == TaskStatus.DONE)
        .group_by(User.id)
        .order_by(func.count(Task.id).desc())
        .limit(5)
    )
    top_reps = (await session.execute(top_reps_q)).all()
    if top_reps:
        top_reps_str = "\n".join(
            f"{idx}. {last} {first} (ID: {uid}): {cnt} задач"
            for idx, (uid, last, first, cnt) in enumerate(top_reps, start=1)
        )
    else:
        top_reps_str = "нет данных"


    freq_row = (await session.execute(freq_q)).first()
    most_freq_interview = freq_row[0] if freq_row else "нет данных"

    month_name_ru = format_date(dt.datetime.now(), "LLLL", locale="ru").capitalize()
    
    await temp_msg.delete()
    await call.message.answer(
        f"Аналитика за {month_name_ru}:\n"
        f"• Визитов: {visits_cnt}\n"
        f"• Кредитов: {credits_cnt}\n"
        f"• Наиболее частый ответ на вопрос 'Как часто клиенты оформляют кредит через ОТП?': {most_freq_interview}\n"
        f"• Процент рекламных материалов: {marketing_percent:.2f}%\n"
        f"• Топ-5 репортёров по завершённым задачам:\n"
        f"{top_reps_str}",
        reply_markup=delete_msg_kb()
    )


# список партнёров
@router.callback_query(F.data == "admin_partners")
async def show_partners(call: CallbackQuery, session: AsyncSession):
    tmp = await call.message.answer("Загружаю партнёров…")

    partners = (await session.execute(select(Partner))).scalars().all()
    if not partners:
        text = "Партнёры ещё не добавлены."
    else:
        lines = [
            f"{idx}. {p.name} — {p.address or 'адрес не указан'}"
            for idx, p in enumerate(partners, 1)
        ]
        text = "Список партнёров:\n" + "\n".join(lines)

    await tmp.delete()
    await call.message.answer(text, reply_markup=admin_partners_kb())


class AddPartner(StatesGroup):
    NAME    = State()
    ADDRESS = State()
    PHONE   = State()


@router.callback_query(F.data == "add_partner")
async def add_partner(cb: CallbackQuery, state: FSMContext):
    """Старт: просим название фирмы."""
    await cb.message.answer(
        "Добавление партнёра.\n\n"
        "Шаг 1/3 — введите название точки:",
        reply_markup=delete_msg_kb()
    )
    await state.set_state(AddPartner.NAME)
    await cb.answer()           # закрыть «часики» на кнопке


@router.message(AddPartner.NAME)
async def partner_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await msg.answer("Шаг 2/3 — укажите адрес:")
    await state.set_state(AddPartner.ADDRESS)


@router.message(AddPartner.ADDRESS)
async def partner_address(msg: Message, state: FSMContext):
    await state.update_data(address=msg.text.strip())
    await msg.answer("Шаг 3/3 — телефон контактного лица (или “—”):")
    await state.set_state(AddPartner.PHONE)


@router.message(AddPartner.PHONE)
async def partner_phone(msg: Message, state: FSMContext, session: AsyncSession):
    tmp_msg = await msg.answer("Добавление партнёра в базу данных...")
    data = await state.get_data()
    phone = msg.text.strip() if msg.text.strip() != "—" else None
    partner = Partner(
        name=data["name"],
        address=data["address"],
        contact_phone=phone,
        active=True,
    )
    session.add(partner)
    await session.commit()
    await tmp_msg.delete()
    await msg.answer("✅ Партнёр успешно добавлен!", reply_markup=delete_msg_kb())
    await state.clear()


STATUS_EMOJI = {
    TaskStatus.PENDING:  "🕓",   # ожидает
    TaskStatus.IN_PROGRESS: "🔄",
    TaskStatus.DONE:     "✅",
    TaskStatus.CANCELED: "🚫",
}


@router.callback_query(F.data == "admin_tasks")
async def admin_tasks(call: CallbackQuery, session: AsyncSession):
    #   Task ←→ Partner (по FK task.partner_id)
    rows = (
        await session.execute(
            select(Task, Partner)
            .join(Partner, Task.partner_id == Partner.id)
            .order_by(Task.due_date)
        )
    ).all()

    if not rows:
        text = "🗂 Задач пока нет."
    else:
        lines = []
        task: Task
        partner: Partner
        for task, partner in rows:
            emoji = STATUS_EMOJI.get(task.status, "❔")
            lines.append(
                f"{emoji} <b>{task.id}</b> · {task.task_type}"         # без .value
                f" • до {task.due_date:%d.%m}\n"
                f"{partner.name} — {partner.address}"
            )
        text = "🗂 <b>Все задачи</b>:\n" + "\n".join(lines)

    await call.message.answer(
        text, parse_mode="HTML",
        reply_markup=admin_tasks_kb()
    )
    await call.answer()


class AddTask(StatesGroup):
    PARTNER  = State()
    REP      = State()
    DUE_DATE = State()
    TYPE     = State()
    DETAILS  = State()
    CONFIRM  = State()


@router.callback_query(F.data == "task_new")
async def task_new(cb: CallbackQuery, session: AsyncSession, state: FSMContext):
    partners = (await session.execute(select(Partner))).scalars().all()
    if not partners:
        await cb.answer("Партнёров нет. Сначала добавьте партнёра.", show_alert=True)
        return

    await cb.message.answer(
        "Шаг 1/5. Выберите партнёра:",
        reply_markup=partners_kb(partners)
    )
    await state.set_state(AddTask.PARTNER)
    await cb.answer()


# ───────── выбор партнёра ─────────
@router.callback_query(AddTask.PARTNER, F.data.startswith("tp_partner_"))
async def w_set_partner(cb: CallbackQuery, state: FSMContext, session: AsyncSession):
    partner_id = int(cb.data.split("_")[2])
    await state.update_data(partner_id=partner_id)

    await cb.message.edit_text(
        "Шаг 2/5. Выберите исполнителя (репортёра):",
        reply_markup=await reps_kb(session)
    )
    await state.set_state(AddTask.REP)
    await cb.answer()


# ───────── выбор исполнителя ─────────
@router.callback_query(AddTask.REP, F.data.startswith("tp_rep_"))
async def w_set_rep(cb: CallbackQuery, state: FSMContext):
    rep_id = int(cb.data.split("_")[2])
    await state.update_data(rep_id=rep_id)

    await cb.message.edit_text(
        "Шаг 3/5. Введите срок задачи:\n"
        "• форматы: <code>20.12.2025</code> / <code>+5</code> (через 5 дней)",
        parse_mode="HTML",
        reply_markup=delete_msg_kb()
    )
    await state.set_state(AddTask.DUE_DATE)
    await cb.answer()


# ───────── ввод срока ─────────
@router.message(AddTask.DUE_DATE)
async def w_set_due(msg: Message, state: FSMContext):
    raw = msg.text.strip()
    try:
        if raw.startswith("+"):
            days = int(raw.lstrip("+"))
            due = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=days)
        else:
            due = dt.datetime.strptime(raw, "%d.%m.%Y").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        await msg.answer("❗ Неверная дата. Попробуйте ещё раз.")
        return

    await state.update_data(due_date=due)
    await msg.answer("Шаг 4/5. Выберите тип задачи:", reply_markup=task_types_kb())
    await state.set_state(AddTask.TYPE)


# ───────── выбор типа ─────────
@router.callback_query(AddTask.TYPE, F.data.startswith("tp_type_"))
async def w_set_type(cb: CallbackQuery, state: FSMContext):
    t_type = cb.data.split("_")[2]  # MERCH / VISIT / CALL
    await state.update_data(task_type=t_type)

    await cb.message.edit_text(
        "Шаг 5/5. Опишите задачу (или пришлите «—»):",
        reply_markup=delete_msg_kb()
    )
    await state.set_state(AddTask.DETAILS)
    await cb.answer()


# ───────── ввод деталей ─────────
@router.message(AddTask.DETAILS)
async def w_details(msg: Message, state: FSMContext):
    await state.update_data(details=None if msg.text.strip() == "—" else msg.text.strip())

    data = await state.get_data()
    summary = (
        "<b>Проверьте данные:</b>\n"
        f"• Партнёр ID {data['partner_id']}\n"
        f"• Исполнитель ID {data['rep_id']}\n"
        f"• Срок: {data['due_date']:%d.%m.%Y}\n"
        f"• Тип: {data['task_type']}\n"
        f"• Описание: {data['details'] or '—'}"
    )
    await msg.answer(summary, parse_mode="HTML", reply_markup=confirm_kb())
    await state.set_state(AddTask.CONFIRM)


# ───────── отмена ─────────
@router.callback_query(AddTask.CONFIRM, F.data == "tp_cancel")
async def w_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("❌ Создание задачи отменено.")
    await cb.answer()


# ───────── подтверждение и запись в БД ─────────
@router.callback_query(AddTask.CONFIRM, F.data == "tp_ok")
async def w_save(cb: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    now_aware = dt.datetime.now(timezone.utc)
    now_naive = now_aware.replace(tzinfo=None)

    due_aware = data["due_date"]                # вы получили её из ввода
    due_naive = due_aware.replace(tzinfo=None)  # убираем tzinfo
    task = Task(
        rep_id      = data["rep_id"],              # ← задайте исполнителя
        partner_id  = data["partner_id"],
        task_type   = TaskType[data["task_type"]],
        due_date    = due_naive,
        status      = TaskStatus.PENDING,
        details     = data["details"],
        created_at  = now_naive,
        updated_at  = now_naive,
    )
    session.add(task)
    await session.commit()

    await cb.message.edit_text("✅ Задача сохранена.")
    await state.clear()
    await cb.answer()