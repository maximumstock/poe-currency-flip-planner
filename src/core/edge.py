from src.core.offer import Offer


class Edge(Offer):
    paid: int
    received: int

    def __init__(self, offer: Offer, received: int, paid: int):
        super().__init__(league=offer.league, want=offer.want, have=offer.have,
                         contact_ign=offer.contact_ign, conversion_rate=offer.conversion_rate, stock=offer.stock)
        self.received = received
        self.paid = paid
