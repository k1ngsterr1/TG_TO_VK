from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from httpx import AsyncClient

from ..fsm import FSM
from ..relations import Relations

router = Router()


@router.message(Command(commands=["add"]))
async def add(m: Message, state: FSMContext):
    await state.set_state(FSM.wait_tg_channels)
    await m.answer("Для внесения идентификаторов (ID) телеграмм-каналов, пожалуйста, сначала добавьте данного бота в соответствующие каналы и выдайте права администратора. Чтобы получить ID канала, воспользуйтесь услугами бота @getmyid_bot. Для этого перешлите любой пост из нужного канала на сообщение этого бота, и он выдаст вам необходимый идентификатор.\n"
                   "Формат: 1,2,3")


@router.message(FSM.wait_tg_channels)
async def add(m: Message, state: FSMContext):
    await state.set_data({"tg_channels": m.text})
    await m.answer("Введите токен аккаунта VK для авторизации. Для получения токена воспользуйтесь услугами этого сервиса  https://vkhost.github.io/, рекомендую использовать приложение (VK Admin)\n"
                   "Формат: abc")
    await state.set_state(FSM.wait_vk_token)


@router.message(FSM.wait_vk_token)
async def add(m: Message, state: FSMContext, relations: Relations):
    data = await state.get_data()
    tg_channels = data["tg_channels"].split(",")
    vk_token = m.text

    async with AsyncClient(headers={"Authorization": f"Bearer {vk_token}"}) as client:
        r = await client.post(f"https://api.vk.com/method/groups.get?extended=1&filter=editor&v=5.199")
        me_groups = (r.json()).get("response").get("items")
        # me_groups = (r.json())
        print(me_groups)
        if not me_groups:
            await state.clear()
            return m.answer("Нам не удалось получить список ваших групп.")

    vk_groups = [(x["name"], x["id"], vk_token) for x in me_groups]
    await state.update_data(data, vk_all_groups=vk_groups)

    vk_groups_text = ""

    for i, vk_group in enumerate(vk_groups):
        vk_groups_text += f"\n{i}) {vk_group[0]}"

    await m.answer(f"Введите номера идентификаторов (ID) групп VK, которые вы хотите связать с вашими телеграм каналами..\nФормат: 0,1,2\n{vk_groups_text}")
    await state.set_state(FSM.wait_vk_groups)


@router.message(FSM.wait_vk_groups)
async def add(m: Message, state: FSMContext, relations: Relations):
    list_relations = []
    data = await state.get_data()

    tg_channels = data["tg_channels"].split(",")
    vk_all_groups = data["vk_all_groups"]
    vk_select_groups = m.text.split(",")

    # Store 'vk_select_groups' in the state data
    await state.update_data(vk_select_groups=vk_select_groups)

    text_relations = ""

    for tg_channel in tg_channels:
        for vk_select_group in vk_select_groups:
            vk_group = vk_all_groups[int(vk_select_group)]
            list_relations.append((tg_channel, *vk_group))
            text_relations += f"\n{tg_channel} -> {vk_group[0]}"
            relations.add(tg_channel, vk_group, 0)  # Add vk_group and 0 here

    await m.answer("Выберите каким образом репостить посты:\n"
                   "1 - только в группе,\n"
                   "2 - только на своей странице,\n"
                   "3 - в группу и на страницу.")
    await state.set_state(FSM.wait_post_choice)  # Switch to the new FSM state


@router.message(FSM.wait_post_choice)
async def add(m: Message, state: FSMContext, relations: Relations):
    list_relations = []
    data = await state.get_data()
    tg_channels = data["tg_channels"].split(",")
    vk_all_groups = data["vk_all_groups"]
    vk_select_groups = data["vk_select_groups"]  # Fixed variable name, removed .split(",")

    text_relations = ""

    for tg_channel in tg_channels:
        for vk_select_group in vk_select_groups:
            vk_select_group = int(vk_select_group)  # Convert to integer
            vk_group = vk_all_groups[vk_select_group]
            where_to_post = int(m.text)
            list_relations.append((tg_channel, vk_group, where_to_post))
            text_relations += f"\n{tg_channel} -> {vk_group[0]}"
            relations.add(tg_channel, vk_group, where_to_post)  # Add new_tuple here

    await m.answer(f"Связь ТГ -> ВК, установлена:\n{text_relations}\n\nЕсли вы решите избавиться от связки, просто удалите телеграм бота из вашего канала.")
    await state.clear()

