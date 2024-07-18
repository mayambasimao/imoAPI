from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.models import visit_requests, short_rentals
from schemas.schema import VisitRequestt, ShortRental
from config.dependencies import is_agent
from typing import List

agent_router = APIRouter()

# Endpoint para visualizar todas as visitas pendentes
@agent_router.get("/visits/pending", response_model=List[VisitRequestt])
def get_pending_visits_agent(agent: dict = Depends(is_agent)):
    try:
        visits_query = select(visit_requests).where(
            visit_requests.c.agent_id == agent["id"],
            visit_requests.c.status == 'pending'
        )
        result = conn.execute(visits_query).fetchall()

        visits_list = []
        for visit in result:
            visit_dict = {
                "id": visit.id,
                "house_id": visit.house_id,
                "client_id": visit.client_id,
                "agent_id": visit.agent_id,
                "scheduled_time": visit.scheduled_time,
                "status": visit.status
            }
            visits_list.append(VisitRequestt(**visit_dict))

        return visits_list
    except SQLAlchemyError as e:
        print(f"Erro ao buscar visitas pendentes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Endpoint para aceitar ou rejeitar um pedido de visita
@agent_router.put("/visits/{visit_id}/status", response_model=VisitRequestt)
def update_visit_status(visit_id: int, status: str, agent: dict = Depends(is_agent)):
    try:
        visit_query = select(visit_requests).where(visit_requests.c.id == visit_id)
        visit = conn.execute(visit_query).fetchone()

        if not visit:
            raise HTTPException(status_code=404, detail="Visita não encontrada")

        if visit.agent_id != agent["id"]:
            raise HTTPException(status_code=403, detail="Você não tem acesso para atualizar esta visita")

        update_visit_query = (
            update(visit_requests)
            .where(visit_requests.c.id == visit_id)
            .values(status=status)
        )
        conn.execute(update_visit_query)
        conn.commit()

        updated_visit = conn.execute(visit_query).fetchone()

        updated_visit_dict = {
            "id": updated_visit.id,
            "house_id": updated_visit.house_id,
            "client_id": updated_visit.client_id,
            "agent_id": updated_visit.agent_id,
            "scheduled_time": updated_visit.scheduled_time,
            "status": updated_visit.status
        }

        return VisitRequestt(**updated_visit_dict)
    except SQLAlchemyError as e:
        print(f"Erro ao atualizar o status da visita: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Endpoint para visualizar todas as solicitações de short rentals pendentes
@agent_router.get("/short-rentals/pending", response_model=List[ShortRental])
def get_pending_short_rentals(agent: dict = Depends(is_agent)):
    try:
        rentals_query = select(short_rentals).where(
            short_rentals.c.agent_id == agent["id"],
            short_rentals.c.status == 'pending'
        )
        result = conn.execute(rentals_query).fetchall()

        rentals_list = []
        for rental in result:
            rental_dict = {
                "id": rental.id,
                "house_id": rental.house_id,
                "client_id": rental.client_id,
                "agent_id": rental.agent_id,
                "start_date": rental.start_date,
                "end_date": rental.end_date,
                "status": rental.status
            }
            rentals_list.append(ShortRental(**rental_dict))

        return rentals_list
    except SQLAlchemyError as e:
        print(f"Erro ao buscar short rentals pendentes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Endpoint para aceitar ou rejeitar uma solicitação de short rental
@agent_router.put("/short-rentals/{rental_id}/status", response_model=ShortRental)
def update_short_rental_status(rental_id: int, status: str, agent: dict = Depends(is_agent)):
    try:
        rental_query = select(short_rentals).where(short_rentals.c.id == rental_id)
        rental = conn.execute(rental_query).fetchone()

        if not rental:
            raise HTTPException(status_code=404, detail="Short rental não encontrado")

        if rental.agent_id != agent["id"]:
            raise HTTPException(status_code=403, detail="Você não tem acesso para atualizar este short rental")

        update_rental_query = (
            update(short_rentals)
            .where(short_rentals.c.id == rental_id)
            .values(status=status)
        )
        conn.execute(update_rental_query)
        conn.commit()

        updated_rental = conn.execute(rental_query).fetchone()

        updated_rental_dict = {
            "id": updated_rental.id,
            "house_id": updated_rental.house_id,
            "client_id": updated_rental.client_id,
            "agent_id": updated_rental.agent_id,
            "start_date": updated_rental.start_date,
            "end_date": updated_rental.end_date,
            "status": updated_rental.status
        }

        return ShortRental(**updated_rental_dict)
    except SQLAlchemyError as e:
        print(f"Erro ao atualizar o status do short rental: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Endpoint para visualizar todas as visitas e short rentals associados ao agente
@agent_router.get("/all-activities", response_model=dict)
def get_all_activities(agent: dict = Depends(is_agent)):
    try:
        # Obter todas as visitas associadas ao agente
        visits_query = select(visit_requests).where(visit_requests.c.agent_id == agent["id"])
        visits_result = conn.execute(visits_query).fetchall()

        visits_list = []
        for visit in visits_result:
            visit_dict = {
                "id": visit.id,
                "house_id": visit.house_id,
                "client_id": visit.client_id,
                "agent_id": visit.agent_id,
                "scheduled_time": visit.scheduled_time,
                "status": visit.status
            }
            visits_list.append(VisitRequestt(**visit_dict))

        # Obter todos os short rentals associados ao agente
        rentals_query = select(short_rentals).where(short_rentals.c.agent_id == agent["id"])
        rentals_result = conn.execute(rentals_query).fetchall()

        rentals_list = []
        for rental in rentals_result:
            rental_dict = {
                "id": rental.id,
                "house_id": rental.house_id,
                "client_id": rental.client_id,
                "agent_id": rental.agent_id,
                "start_date": rental.start_date,
                "end_date": rental.end_date,
                "status": rental.status
            }
            rentals_list.append(ShortRental(**rental_dict))

        return {"visits": visits_list, "short_rentals": rentals_list}
    except SQLAlchemyError as e:
        print(f"Erro ao buscar atividades do agente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

