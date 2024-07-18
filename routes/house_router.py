from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from models.models import houses
from schemas.schema import House, HouseCreate, HouseUpdate
from config.db import conn
from config.dependencies import is_seller, is_agent
from typing import List


house_router = APIRouter()

#ROTA PARA UM VENDEDOR CRIAR UMA CASA E ASSOCIAR A UM AGENTE IMOBILIARIO
@house_router.post("/houses", response_model=House)
def create_house(house: HouseCreate, seller: dict = Depends(is_seller)):
    try:
        new_house = houses.insert().values(
            title=house.title,
            description=house.description,
            price=house.price,
            type_transaction=house.type_transaction,
            seller_id=seller['id'],
            agent_id=house.agent_id,
            assignment_status='pending'
        )
        result = conn.execute(new_house)
        conn.commit()
        
        house_id = result.lastrowid
        query = select(houses).where(houses.c.id == house_id)
        created_house = conn.execute(query).first()
        
        # Convertendo o objeto Row em um dicionário manualmente
        created_house_dict = {
            "id": created_house.id,
            "title": created_house.title,
            "description": created_house.description,
            "price": created_house.price,
            "type_transaction": created_house.type_transaction,
            "status": created_house.status,
            "seller_id": created_house.seller_id,
            "agent_id": created_house.agent_id,
            "assignment_status": created_house.assignment_status
        }
        
        return House(**created_house_dict)
        
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#ROTA PARA EXIBIR TODAS AS CASAS GERENCIADAS POR UM DETERMINADO VENDEDOR      
@house_router.get("/houses/seller", response_model=List[House])
def get_houses_by_seller(seller: dict = Depends(is_seller)):
    try:
        houses_query = select(houses).where(houses.c.seller_id == seller['id'])
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
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ROTA PARA UM VENDEDOR REMOVER UMA CASA QUE ELE REGISTROU
@house_router.delete("/houses/{house_id}", response_model=House)
def delete_house(house_id: int, seller: dict = Depends(is_seller)):
    try:
        house_query = select(houses).where(houses.c.id == house_id)
        house = conn.execute(house_query).first()

        if not house:
            raise HTTPException(status_code=404, detail="House not found")

        if house.seller_id != seller['id']:
            raise HTTPException(status_code=403, detail="You do not have access to update this house")

        deleted_house_dict = {
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
        
        delete_house_query = delete(houses).where(houses.c.id == house_id)
        conn.execute(delete_house_query)
        conn.commit()

        return House(**deleted_house_dict)
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ROTA PARA UM VENDEDOR ATUALIZAR UMA CASA QUE ELE REGISTROU
@house_router.put("/houses/{house_id}", response_model=House)
def update_house(house_id: int, house_update: HouseUpdate, seller: dict = Depends(is_seller)):
    try:
        house_query = select(houses).where(houses.c.id == house_id)
        house = conn.execute(house_query).first()

        if not house:
            raise HTTPException(status_code=404, detail="House not found")

        if house.seller_id != seller['id']:
            raise HTTPException(status_code=403, detail="You do not have access to update this house")

        
        update_values = {}
        for field, value in house_update.dict(exclude_unset=True).items():
            update_values[field] = value

        updated_house_query = (
            update(houses)
            .where(houses.c.id == house_id)
            .values(update_values)
        )
         
        conn.execute(updated_house_query)
        conn.commit()

        updated_house = conn.execute(house_query).first()

        updated_house_dict = {
            "id": updated_house.id,
            "title": updated_house.title,
            "description": updated_house.description,
            "price": updated_house.price,
            "type_transaction": updated_house.type_transaction,
            "status": updated_house.status,
            "seller_id": updated_house.seller_id,
            "agent_id": updated_house.agent_id,
            "assignment_status": updated_house.assignment_status
        }

        return House(**updated_house_dict)
    
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#ROTA PARA AGENTE IMOBILIARIO ACEITAR OU RECUSAR UMA CASA
@house_router.put("/houses/{house_id}/status", response_model=House)
def update_house_status(house_id: int, status: str, agent: dict = Depends(is_agent)):
    try:
        house_query = select(houses).where(houses.c.id == house_id)
        house = conn.execute(house_query).first()

        if not house:
            raise HTTPException(status_code=404, detail="House not found")

        if house.agent_id != agent['id']:
            raise HTTPException(status_code=403, detail="You do not have access to update this house")

        updated_house_query = (
            update(houses)
            .where(houses.c.id == house_id)
            .values(assignment_status=status)
        )
        conn.execute(updated_house_query)
        conn.commit()

        updated_house = conn.execute(house_query).first()

        if not updated_house:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated house")

        updated_house_dict = {
            "id": updated_house.id,
            "title": updated_house.title,
            "description": updated_house.description,
            "price": updated_house.price,
            "type_transaction": updated_house.type_transaction,
            "status": updated_house.status,
            "seller_id": updated_house.seller_id,
            "agent_id": updated_house.agent_id,
            "assignment_status": updated_house.assignment_status
        }

        return House(**updated_house_dict)
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
#ROTA PARA EXIBIR TODAS AS CASAS GERENCIADAS POR UM DETERMINADO AGENTE    
@house_router.get("/houses/agent", response_model=List[House])
def get_houses_by_agent(agent: dict = Depends(is_agent)):
    try:
        houses_query = select(houses).where(houses.c.agent_id == agent['id'])
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
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")   


    
    
    
    
    
    
    