" FSM‑сценарий отчёта о визите. "
from aiogram import Router, F
from aiogram.enums import ContentType      
from aiogram.filters import Command 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ContentType

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.report import marketing_kb, get_tasks_kb, continue_kb
from models import Visit, Task, Partner, Report as ReportORM, User
from models.enums import TaskStatus, Marketing
from .start import cmd_start

router = Router()

class Report(StatesGroup):
    CONTINUE = State()
    PHOTO = State()
    MARKETING = State()
    INTERVIEW = State()
    SHARE = State()
    COMPETITORS = State()
    COMMENT = State()
    FINISH = State()

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    await message.answer("Отчёт отменён")
    await cmd_start(message, session)

@router.callback_query(F.data == "start_report")
async def start_report(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text("Выберите место для отчёта: ", reply_markup=await get_tasks_kb())
    await state.update_data(base_msg=msg)

@router.callback_query(F.data.startswith("task_"))
async def task_selected(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    prev_msg: Message = await state.get_value("base_msg")
    await prev_msg.edit_text("Загрузка информации о задаче...")
    task_id = int(call.data.split("_")[1])
    stmt = (
        select(Task, Partner)
        .join(Partner, Task.partner_id == Partner.id)
        .where(Task.id == task_id)
    )
    rows = (await session.execute(stmt)).first()    # list[tuple[Task, Partner]]
    if rows and rows[0].status == TaskStatus.IN_PROGRESS:
        task: Task = rows[0]
        partner: Partner = rows[1]
        await prev_msg.edit_text(
            f"Выбранная задача: {task.task_type}\n"
            f"Партнёр: {partner.name}\n"
            f"Адрес: {partner.address}\n"
            f"Имя контактного лица: {partner.contact_name}\n"
            f"Телефон: {partner.contact_phone}\n"
            f"Желаете продолжить? (да/нет)",
            reply_markup=continue_kb()
        )
        await state.update_data(task_id=task.id)
        await state.update_data(partner_id=partner.id)
        await state.set_state(Report.CONTINUE)
    else:
        await prev_msg.edit_text("Задача не найдена или уже завершена.")
        return
    

@router.callback_query(Report.CONTINUE, F.data.startswith("continue_"))
async def continue_report(call: CallbackQuery, state: FSMContext):
    prev_msg: Message = await state.get_value("base_msg")
    if call.data == "continue_yes":
        await prev_msg.edit_text("Отчёт о визите начат")
        await state.set_state(Report.PHOTO)
        await call.message.answer("📸 Пришлите 1–2 фото витрины с рекламой ОТП")
    else:
        await prev_msg.edit_text("Отчёт отменён.")
        await state.clear()
        await cmd_start(call.message)


_album_cache: dict[str, list[str]] = defaultdict(list)

@router.message(Report.PHOTO, F.content_type == ContentType.PHOTO)
async def photo_received(msg: Message, state: FSMContext):

    best_id = msg.photo[-1].file_id            # наилучший размер :contentReference[oaicite:0]{index=0}

    if msg.media_group_id:                     # ← альбом
        bucket = _album_cache[msg.media_group_id]   # получаем список
        bucket.append(best_id)

        if len(bucket) < 2:                    # ждём второе фото
            return

        photos = bucket[:2]                    # 1 или 2 file_id
        _album_cache.pop(msg.media_group_id, None)  # чистим кэш
    else:                                      # ← обычное одиночное фото
        photos = [best_id]

    # сохраняем file_id-ы в FSM и переходим дальше
    await state.update_data(photos=photos)
    await state.set_state(Report.MARKETING)
    await msg.answer(
        "Есть ли рекламные материалы ОТП на месте?",
        reply_markup=marketing_kb(),
    )


@router.callback_query(Report.MARKETING, F.data.startswith("mkt_"))
async def marketing_answer(call: CallbackQuery, state: FSMContext):
    await state.update_data(marketing=call.data.split("_")[1])
    await state.set_state(Report.INTERVIEW)
    await call.message.answer("Как часто клиенты оформляют кредит через ОТП? (короткий ответ)")

@router.message(Report.INTERVIEW)
async def interview_answer(msg: Message, state: FSMContext):
    await state.update_data(interview=msg.text)
    await state.set_state(Report.SHARE)
    await msg.answer("Сколько клиентов взяли кредит в этом месяце? (число)")

@router.message(Report.SHARE)
async def share_answer(msg: Message, state: FSMContext):
    await state.update_data(share=msg.text)
    await state.set_state(Report.COMPETITORS)
    await msg.answer("Какие другие банки оформляют кредиты? Напишите через запятую")

@router.message(Report.COMPETITORS)
async def competitors_answer(msg: Message, state: FSMContext):
    await state.update_data(competitors=msg.text)
    await state.set_state(Report.COMMENT)
    await msg.answer("Что ещё нужно учесть? (комментарий)")

@router.message(Report.COMMENT)
async def comment_answer(msg: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    data["comment"] = msg.text
    temp_msg = await msg.answer("Отправка отчёта...")

    report = ReportORM(
        photos_list=",".join(data["photos"]),
        marketing=Marketing(data["marketing"]).value,
        interview=data["interview"],
        share=int(data["share"]),
        competitors=data["competitors"],
        comment=data["comment"],
        task_id=data["task_id"],
    )
    session.add(report)
    await session.flush()

    repr_id = select(User.id).where(User.telegram_id == msg.from_user.id)
    visit = Visit(
        rep_id=repr_id,
        partner_id=data["partner_id"],
        visited_at=msg.date,
        notes=data["comment"],
        report_id=report.id,
    )
    session.add(visit)
    await session.commit()

    await temp_msg.edit_text("Спасибо! Отчёт успешно отправлен ✅")
    await state.clear()
