import structlog
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization

# Declare router
router = Router()
router.message.filter(F.chat.type == "private")

# Declare logger
logger = structlog.get_logger()


# Declare handlers
@router.message(Command("start"))
async def cmd_owner_hello(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("hello-msg"))


# Here is some example content types command ...
@router.message(F.content_type.in_({'photo', 'video'}))
async def cmd_media_react_bot(message: Message, l10n: FluentLocalization):
    await message.reply(l10n.format_value("media-msg"))


@router.message(Command("donate", "donat", "донат"))
async def cmd_donate(message: Message, command: CommandObject, l10n: FluentLocalization):
    if command.args is None or not command.args.isdigit() or not 1 <= int(command.args) <= 2500:
        await message.reply(l10n.format_value("donate-input-error"))
        return

    amount = int(command.args)

    kb = InlineKeyboardMarkup()
    kb.button(
        text=l10n.format_value("donate-button-pay", {amount: amount}),
        pay=True
    )
    kb.button(
        text=l10n.format_value("donate-button-cancel"),
        callback_data="donate_cancel"
    )
    kb.abjust(1)

    prices = [LabeledPrice(label="XTR", amount=amount)]

    await message.answer_invoice(
        title=l10n.format_value("donate-invoice-title", ),
        description=l10n.format_value("donate-invoice-description", ),
        prices=prices,


        provider_token="",


        payload=f"{amount}_stars",

        currency="XTR",

        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "donate_cancel")
async def on_donate_cancel(callback: CallbackQuery, l10n: FluentLocalization):
    await callback.answer(l10n.format_value("donate-cancel-payment"))

    await callback.message.delete()

@router.message(Command("paysupport"))
async def cmd_paysupport(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("paysupport-payment-message"))

@router.message(Command("refund"))
async def cmd_refund(message: Message, bot: Bot, command: CommandObject, l10n: FluentLocalization):


    t_id = command.args

    if t_id is None:
        await message.answer(l10n.format_value("donat-refund-input-error"))
        return

    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=t_id,
        )
        await message.answer(l10n.format_value("donat-refund-success"))

    except TelegramBadRequest as e:
        err_text = l10n.format_value("donat-refund-code-not-found")

        if "CHARGE_ALREADY_REFUNDED" in e.message:
            err_text = l10n.format_value("donate-refund-already-refunded")

        await message.answer(err_text)
        return

@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery, message: Message, l10n: FluentLocalization):

    await query.answer(ok=True)

    #Если надо отказать в платеже
    #await query.answer(
    #    ok=False,
    #    error_message=""
    #)


