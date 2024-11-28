# pessoa.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Pessoa(Base):
    __abstract__ = True  
    id = Column(Integer, primary_key=True)
    nome = Column(String)

    def __init__(self, id, nome):
        self.id = id
        self.nome = nome

class Diretor(Pessoa):
    __tablename__ = 'diretores'
    filmes = relationship("Filme", back_populates="diretor")

class Ator(Pessoa):
    __tablename__ = 'atores'
    filmes = relationship("Filme", secondary='filme_ator', back_populates="atores")
