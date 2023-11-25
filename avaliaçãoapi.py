from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI()

class Cliente(BaseModel):
    id: int
    nome: str
    tipo_atendimento: str

class ClienteNaFila(BaseModel):
    posicao: int
    nome: str
    data_chegada: datetime
    atendido: bool
    tipo_atendimento: str

db_cliente_fila = [
    Cliente(id=1, nome="Hellen Sanches", tipo_atendimento="N"),
    Cliente(id=2, nome="Sidney Jr", tipo_atendimento="P"),
    Cliente(id=3, nome="Maria Beatriz", tipo_atendimento="N"),
    Cliente(id=4, nome="Dalva Laver", tipo_atendimento="P"),
    Cliente(id=5, nome="Valentina Reis", tipo_atendimento="N"),
    Cliente(id=6, nome="Joca Laver", tipo_atendimento="N")
]

fila = []


def adicionar_cliente_na_fila(cliente):
    if cliente["tipo_atendimento"] == "P":
        posicao = 1
        for c in fila:
            if c["tipo_atendimento"] == "P":
                posicao += 1
        fila.insert(posicao - 1, cliente)
    else:
        fila.append(cliente)

for cliente in db_cliente_fila:
    cliente_info = {
        "id": cliente.id,
        "nome": cliente.nome,
        "tipo_atendimento": cliente.tipo_atendimento,
        "data_chegada": datetime.now(),
        "atendido": False
    }
    adicionar_cliente_na_fila(cliente_info)


@app.get('/fila', response_model=List[ClienteNaFila])
def get_fila():
    clientes_na_fila = [
        {"posicao": index + 1, "nome": cliente["nome"], "data_chegada": cliente["data_chegada"],
         "atendido": cliente["atendido"], "tipo_atendimento": cliente["tipo_atendimento"]}
        for index, cliente in enumerate(fila)
        if not cliente["atendido"]
    ]

    return clientes_na_fila


@app.get('/fila/{id}', response_model=dict)
def get_cliente_na_fila(id: int):
    if id <= 0 or id > len(fila) or fila[id - 1]["atendido"]:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    cliente = fila[id - 1]
    return {"posicao": id, "nome": cliente["nome"], "dataChegada": cliente["data_chegada"]}


@app.post('/fila', response_model=dict)
def adicionar_cliente(cliente: Cliente):
    if len(cliente.nome) > 20 or cliente.tipo_atendimento not in ['N', 'P']:
        raise HTTPException(status_code=400, detail="Parâmetros inválidos.")

    novo_cliente = {
        "nome": cliente.nome,
        "tipo_atendimento": cliente.tipo_atendimento,
        "data_chegada": datetime.now(),
        "atendido": False
    }

    adicionar_cliente_na_fila(novo_cliente)

    return {"posicao": len(fila), "nome": novo_cliente["nome"], "dataChegada": novo_cliente["data_chegada"]}


@app.put('/fila', response_model=dict)
def atender_proximo():
    if not fila:
        return []

    cliente_atendido = fila.pop(0)
    cliente_atendido["atendido"] = True

    return {"posicao": 0, "nome": cliente_atendido["nome"], "dataChegada": cliente_atendido["data_chegada"], "atendido": True}


@app.delete('/fila/{id}', status_code=204)
def remover_cliente_na_fila(id: int):
    if id <= 0 or id > len(fila):
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    fila.pop(id - 1)
