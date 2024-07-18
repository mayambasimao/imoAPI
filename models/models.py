from sqlalchemy import Table, Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
from config.db import meta, engine
from sqlalchemy.orm import relationship

assignment_status = Enum('pending', 'accepted', 'rejected', name='assignment_status')
visit_status = Enum('pending', 'approved', 'rejected', name='visit_status')

#Role: vendedor, cliente, agenteImob, ted, servicosEsp, interBanc, parceiroTuris

users = Table(
    "users", meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String(150)),
    Column("email", String(150), unique=True),
    Column("password", String(150)),
    Column("role", String(50))
)

houses = Table(
    "houses", meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String(150)),
    Column("description", String(255)),
    Column("price", Float),
    Column("type_transaction", String(50)),  # for sale or for rent
    Column("status", Boolean, default=True),  # available or unavailable
    Column("seller_id", Integer, ForeignKey("users.id")),
    Column("agent_id", Integer, ForeignKey("users.id")),
    Column("assignment_status", assignment_status, default='pending')
)

visit_requests = Table(
    "visit_requests", meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("house_id", Integer, ForeignKey("houses.id")),
    Column("client_id", Integer, ForeignKey("users.id")),
    Column("agent_id", Integer, ForeignKey("users.id")),
    Column("scheduled_time", DateTime),
    Column("status", assignment_status, default='pending') # Estado da solicitação de visita
)

short_rentals = Table(
    "short_rentals", meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("house_id", Integer, ForeignKey("houses.id")),
    Column("client_id", Integer, ForeignKey("users.id")),
    Column("agent_id", Integer, ForeignKey("users.id")),
    Column("start_date", DateTime),
    Column("end_date", DateTime),
    Column("status", assignment_status, default='pending')  # pending, accepted, rejected
)

meta.create_all(engine)