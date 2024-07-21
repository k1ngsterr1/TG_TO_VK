import json

from cfg import DIR_RELATIONS


class Relations:
    @classmethod
    def read(cls) -> dict:
        with open(DIR_RELATIONS, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def add(self, tg_channel: str, vk_group: tuple, where_to_post: int) -> dict:
        data = self.read()
        if data.get(tg_channel):
            for group in data[tg_channel]:
                if group[0][0] == vk_group[0]:
                    data[tg_channel].remove(group)                
            data[tg_channel].append((vk_group, where_to_post))
        else:
            data[tg_channel] = [(vk_group, where_to_post)]
        with open(DIR_RELATIONS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return data
