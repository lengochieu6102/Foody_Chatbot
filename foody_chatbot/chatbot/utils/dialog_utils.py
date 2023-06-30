import copy
def remove_payload(dialog):
    gpt_dialog = copy.deepcopy(dialog)
    for mes in gpt_dialog:
        if type(mes["content"]) == dict:
            mes["content"] = mes["content"]["text"]
    return gpt_dialog