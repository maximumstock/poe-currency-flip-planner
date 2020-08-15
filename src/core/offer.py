from dataclasses import dataclass


@dataclass
class Offer:
    league: str
    have: str
    want: str
    contact_ign: str
    conversion_rate: float
    stock: int

    @classmethod
    def from_offer(cls, offer):
        return cls(league=offer.league,
                   have=offer.have,
                   want=offer.want,
                   contact_ign=offer.contact_ign,
                   conversion_rate=offer.conversion_rate,
                   stock=offer.stock)

    @classmethod
    def from_parts(cls, league, have, want, contact_ign, conversion_rate,
                   stock):
        return cls(league=league,
                   have=have,
                   want=want,
                   contact_ign=contact_ign,
                   conversion_rate=conversion_rate,
                   stock=stock)
