from aiogram.filters import BaseFilter
from aiogram.types import Message

class MemberCanRestrictFilter(BaseFilter):

    def __init__(self, member_can_restrict: bool):
        self.member_can_restrict = member_can_restrict

    async def __call__(self, message: Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)


        return (member.is_chat_creator() or member.can_restrict_members) == self.member_can_restrict
