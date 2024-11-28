# filme.py

from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


filme_ator = Table(
    'filme_ator', Base.metadata,
    Column('filme_id', Integer, ForeignKey('filmes.id')),
    Column('ator_id', Integer, ForeignKey('atores.id'))
)

class Filme(Base):
    __tablename__ = 'filmes'

    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    avaliacao = Column(Float)
    data_lancamento = Column(String)
    generos = Column(String)
    poster_path = Column(String)
    budget = Column(Float)  
    revenue = Column(Float)  
    diretor_id = Column(Integer, ForeignKey('diretores.id'))
    diretor = relationship("Diretor", back_populates="filmes")
    atores = relationship("Ator", secondary=filme_ator, back_populates="filmes")

    def __init__(self, id, titulo, avaliacao, data_lancamento, generos, poster_path, budget=None, revenue=None):
        self.id = id
        self.titulo = titulo
        self.avaliacao = avaliacao
        self.data_lancamento = data_lancamento
        self.generos = generos
        self.poster_path = poster_path
        self.budget = budget 
        self.revenue = revenue  

    def exibir_info(self):
        print(f'Título: {self.titulo}, Avaliação: {self.avaliacao}, Orçamento: {self.budget}, Receita: {self.revenue}')

