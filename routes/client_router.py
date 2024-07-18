from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from datetime import datetime
from schemas.schema import VisitRequest, House,  ShortRental, ShortRentalCreate, VisitRequestt
from config.db import conn
from models.models import houses, visit_requests, short_rentals
from config.dependencies import is_client
from typing import List

client_router = APIRouter()

# Endpoint para um cliente visualizar todas as casas
@client_router.get("/houses", response_model=List[House])
def get_all_houses_client(current_user: dict = Depends(is_client)):
    try:
        houses_query = select(houses)
        result = conn.execute(houses_query).fetchall()

        houses_list = []
        for house in result:
            house_dict = {
                "id": house.id,
                "title": house.title,
                "description": house.description,
                "price": house.price,
                "type_transaction": house.type_transaction,
                "status": house.status,
                "seller_id": house.seller_id,
                "agent_id": house.agent_id,
                "assignment_status": house.assignment_status
            }
            houses_list.append(House(**house_dict))

        return houses_list
    except SQLAlchemyError as e:
        print(f"Erro ao buscar casas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
    
# Endpoint para um cliente solicitar uma visita a uma casa
@client_router.post("/visit-request", response_model=VisitRequest)
def request_visit(visit_request: VisitRequest, current_user: dict = Depends(is_client)):
    try:
        # Verifica se o usuário atual é um cliente
        if current_user["role"] != "cliente":
            raise HTTPException(status_code=403, detail="Somente clientes podem solicitar visitas.")

        # Verifica se a casa existe e recupera o agente associado
        house_query = select(houses).where(houses.c.id == visit_request.house_id)
        house = conn.execute(house_query).fetchone()
        if not house:
            raise HTTPException(status_code=404, detail=f"Casa com ID {visit_request.house_id} não encontrada.")
        
        house_dict = dict(house._mapping)  # Converte Row para dicionário
        agent_id = house_dict["agent_id"]

        # Insere a solicitação de visita no banco de dados
        new_visit_request = visit_requests.insert().values(
            house_id=visit_request.house_id,
            client_id=current_user["id"],
            agent_id=agent_id,
            scheduled_time=visit_request.scheduled_time,
            status='pending'
        )
        result = conn.execute(new_visit_request)
        conn.commit()
        
        visit_request_id = result.lastrowid
        
        # Retorna a solicitação de visita criada
        return {**visit_request.dict(), "id": visit_request_id, "agent_id": agent_id, "status": 'pending'}

    except SQLAlchemyError as e:
        print(f"Erro ao solicitar visita: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Endpoint para visualizar todas as visitas pendentes
@client_router.get("/visits", response_model=List[VisitRequestt])
def get_all_visits_client(current_user: dict = Depends(is_client)):
    try:
        visits_query = select(visit_requests).where(
            visit_requests.c.client_id == current_user["id"]
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


# Endpoint para um cliente visualizar todas as casas para arrendar
@client_router.get("/houses/for-rent", response_model=List[House])
def get_houses_for_rent(current_user: dict = Depends(is_client)):
    try:
        houses_query = select(houses).where(houses.c.type_transaction == 'arrendar')
        result = conn.execute(houses_query).fetchall()

        houses_list = []
        for house in result:
            house_dict = {
                "id": house.id,
                "title": house.title,
                "description": house.description,
                "price": house.price,
                "type_transaction": house.type_transaction,
                "status": house.status,
                "seller_id": house.seller_id,
                "agent_id": house.agent_id,
                "assignment_status": house.assignment_status
            }
            houses_list.append(House(**house_dict))

        return houses_list
    except SQLAlchemyError as e:
        print(f"Erro ao buscar casas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Endpoint para um cliente visualizar todas as casas para vender
@client_router.get("/houses/for-sale", response_model=List[House])
def get_houses_for_sale(current_user: dict = Depends(is_client)):
    try:
        houses_query = select(houses).where(houses.c.type_transaction == 'vender')
        result = conn.execute(houses_query).fetchall()

        houses_list = []
        for house in result:
            house_dict = {
                "id": house.id,
                "title": house.title,
                "description": house.description,
                "price": house.price,
                "type_transaction": house.type_transaction,
                "status": house.status,
                "seller_id": house.seller_id,
                "agent_id": house.agent_id,
                "assignment_status": house.assignment_status
            }
            houses_list.append(House(**house_dict))

        return houses_list
    except SQLAlchemyError as e:
        print(f"Erro ao buscar casas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Endpoint para solicitar short rental
@client_router.post("/short-rentals", response_model=ShortRental)
def request_short_rental(rental_request: ShortRentalCreate, current_user: dict = Depends(is_client)):
    try:
        # Verifica se a casa existe e recupera o agente associado
        house_query = select(houses).where(houses.c.id == rental_request.house_id)
        house = conn.execute(house_query).fetchone()
        if not house:
            raise HTTPException(status_code=404, detail=f"Casa com ID {rental_request.house_id} não encontrada.")
        
        house_dict = dict(house._mapping)  # Converte Row para dicionário
        
        # Verifica se a casa está para arrendar
        if house_dict["type_transaction"] != "arrendar":
            raise HTTPException(status_code=400, detail="Short rentals só podem ser solicitados para casas que estão para arrendar.")
        
        agent_id = house_dict["agent_id"]

        # Insere a solicitação de short rental no banco de dados
        new_rental_request = short_rentals.insert().values(
            house_id=rental_request.house_id,
            client_id=current_user["id"],
            agent_id=agent_id,
            start_date=rental_request.start_date,
            end_date=rental_request.end_date,
            status='pending'
        )
        result = conn.execute(new_rental_request)
        conn.commit()

        rental_request_id = result.lastrowid

        # Retorna a solicitação de short rental criada
        return {**rental_request.dict(), "id": rental_request_id, "client_id": current_user["id"], "agent_id": agent_id, "status": 'pending'}

    except SQLAlchemyError as e:
        print(f"Erro ao solicitar short rental: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Endpoint para visualizar todas as solicitações de short rentals do cliente
@client_router.get("/short-rentals", response_model=List[ShortRental])
def get_short_rentals(current_user: dict = Depends(is_client)):
    try:
        rentals_query = select(short_rentals).where(short_rentals.c.client_id == current_user["id"])
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
        print(f"Erro ao buscar short rentals: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")



