from typing import Dict


class StackSizeHelper:
    stack_sizes: Dict[str, int] = dict({
        "Orb of Alchemy": 10,
        "Regal Orb": 10,
        "Chaos Orb": 10,
        "Vaal Orb": 10,
        "Exalted Orb": 10,
        "Divine Orb": 10,
        "Mirror of Kalandra": 10,
        "Simple Sextant": 10,
        "Prime Sextant": 10,
        "Awakened Sextant": 10,
        "Blacksmith's Whetstone": 20,
        "Chromatic Orb": 20,
        "Orb of Chance": 20,
        "Orb of Alteration": 20,
        "Glassblower's Bauble": 20,
        "Jeweller's Orb": 20,
        "Orb of Fusing": 20,
        "Gemcutter's Prism": 20,
        "Blessed Orb": 20,
        "Orb of Annulment": 20,
        "Cartographer's Chisel": 20,
        "Orb of Augmentation": 30,
        "Orb of Scouring": 30,
        "Armourer's Scrap": 40,
        "Orb of Transmutation": 40,
        "Orb of Regret": 40
    })

    def __init__(self):
        pass

    def get_stack_size(self, name: str) -> int:
        return self.stack_sizes.get(name, 1)

    def get_maximum_volume_for_item(self, name: str) -> int:
        return self.get_stack_size(name) * 12 * 5
