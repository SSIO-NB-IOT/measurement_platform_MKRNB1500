from typing import List, Optional

from sqlalchemy import Float, String,ForeignKey
from sqlalchemy.orm import DeclarativeBase,mapped_column,relationship,Mapped


class Base(DeclarativeBase):
    pass

class Campaign(Base):
    __tablename__ = 'campaigns'

    id :  Mapped[int] = mapped_column(primary_key=True)
    name = mapped_column(String(256))
    description : Mapped[Optional[str]] = mapped_column(String(256))
    missions  : Mapped[List["Mission"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")

class Mission(Base):
    __tablename__ = 'missions'

    id :Mapped[int] = mapped_column(primary_key=True)
    campaign : Mapped["Campaign"] = relationship(back_populates="missions")
    campaign_id : Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    packet_size = mapped_column(Float)
    packet_send_frequency = mapped_column(Float)
    energy_consume = mapped_column(Float)
    packet_delivery_ratio = mapped_column(Float)
    mission_time = mapped_column(Float)
    e_drx_value = mapped_column(Float)
    network_coordination_mode = mapped_column(String(32))
    radio_access_technologies_mode = mapped_column(String(32))
    throughput = mapped_column(Float)