"""FSM‑сценарий отчёта о визите."""
from aiogram import Router, F
from aiogram.enums import ContentType       
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ContentType
from aiogram.exceptions import TelegramBadRequest

from keyboards.report import marketing_kb

router = Router()

class Report(StatesGroup):
    GEO = State()
    PHOTO = State()
    MARKETING = State()
    INTERVIEW = State()
    SHARE = State()
    COMPETITORS = State()
    COMMENT = State()
    FINISH = State()

@router.callback_query(F.data == "start_report")
async def start_report(call: CallbackQuery, state: FSMContext):
    await state.set_state(Report.GEO)
    await call.message.answer("📍 Отправьте геолокацию магазина (кнопка скрепка -> Геопозиция).")

@router.message(Report.GEO, F.content_type == ContentType.LOCATION)
async def geo_received(msg: Message, state: FSMContext):
    await state.set_state(Report.PHOTO)
    await msg.answer("📸 Пришлите 1–2 фото витрины с рекламой ОТП")

@router.message(Report.PHOTO, F.content_type == ContentType.PHOTO)
async def photo_received(msg: Message, state: FSMContext):
    await state.set_state(Report.MARKETING)
    await msg.answer("Есть ли рекламные материалы ОТП на месте?", reply_markup=marketing_kb())

@router.callback_query(Report.MARKETING, F.data.startswith("mkt_"))
async def marketing_answer(call: CallbackQuery, state: FSMContext):
    await state.update_data(marketing=call.data)
    await state.set_state(Report.INTERVIEW)
    await call.message.answer("Как часто клиенты оформляют кредит через ОТП? (короткий ответ)")

@router.message(Report.INTERVIEW)
async def interview_answer(msg: Message, state: FSMContext):
    await state.update_data(interview=msg.text)
    await state.set_state(Report.SHARE)
    await msg.answer("Какую долю кредитов занимает ОТП сегодня? (в %)")

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
async def comment_answer(msg: Message, state: FSMContext):
    data = await state.get_data()
    data["comment"] = msg.text
    # TODO: persist to DB via session in data["session"]
    await msg.answer("Спасибо! Отчёт успешно отправлен ✅")
    await state.clear()