from sqlalchemy import Table, Column, Integer, Float, String, ForeignKey, Boolean
from config.db import meta, engine
from sqlalchemy.orm import relationship


users = Table(
    "users", meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String(150)),
    Column("email", String(150), unique=True),
    Column("password", String(150)),
    Column("role", String(50))
)

servicos_especializados = Table(
    "servicos_especializados", meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("tipo_servico", String(150)),
    Column("descricao", String(250)),
    Column("preco", Integer),
)

parceiros_turisticos = Table(
    "parceiros_turisticos", meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("nome_parceiro", String(150)),
    Column("tipo_servico", String(150)),
    Column("detalhes", String(250)),
)

houses = Table(
   "houses", meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String(150)),
    Column("description", String(255)),
    Column("price", Float),
    Column("type_transaction", String(50)),  # for sale or for rent
    Column("status", Boolean, default=True), # available or unavailable
    Column("seller_id", Integer, ForeignKey("users.id")),
    Column("agent_id", Integer, ForeignKey("users.id"))
)

meta.create_all(engine)