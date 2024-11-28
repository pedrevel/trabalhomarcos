# main.py

from api_tmdb import TMDbAPI
from database import Base, engine, SessionLocal
from filme import Filme
from pessoa import Diretor, Ator
import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import webbrowser


def criar_banco():
    Base.metadata.create_all(engine)


def obter_dados_filmes(api, total_paginas=5):
    session = SessionLocal()
    filmes = [] 

    for page in range(1, total_paginas + 1):
        data = api.get_top_rated_movies(page=page)
        if data is None or 'results' not in data:
            print(f"Falha ao obter dados da página {page}. Pulando para a próxima página.")
            continue

        for item in data['results']:
            movie_id = item['id']

          
            if session.query(Filme).filter_by(id=movie_id).first():
                print(f"Filme ID {movie_id} já existe no banco. Pulando.")
                continue

            detalhes = api.get_movie_details(movie_id)
            api.rate_limit()

            if detalhes is None:
                print(f"Falha ao obter detalhes do filme ID {movie_id}. Pulando para o próximo filme.")
                continue

            titulo = detalhes.get('title')
            avaliacao = detalhes.get('vote_average')
            data_lancamento = detalhes.get('release_date')
            generos = ", ".join([g['name'] for g in detalhes.get('genres', [])])
            poster_path = detalhes.get('poster_path')
            budget = detalhes.get('budget') or None
            revenue = detalhes.get('revenue') or None

            filme = Filme(
                id=movie_id,
                titulo=titulo,
                avaliacao=avaliacao,
                data_lancamento=data_lancamento,
                generos=generos,
                poster_path=poster_path,
                budget=budget,
                revenue=revenue,
            )

          
            with session.no_autoflush:
                crew = detalhes.get('credits', {}).get('crew', [])
                diretor_info = next((p for p in crew if p['job'] == 'Director'), None)
                if diretor_info:
                    diretor = session.query(Diretor).filter_by(id=diretor_info['id']).first()
                    if not diretor:
                        diretor = Diretor(id=diretor_info['id'], nome=diretor_info['name'])
                        session.add(diretor)
                    filme.diretor = diretor

                cast = detalhes.get('credits', {}).get('cast', [])[:5]
                for ator_info in cast:
                    ator = session.query(Ator).filter_by(id=ator_info['id']).first()
                    if not ator:
                        ator = Ator(id=ator_info['id'], nome=ator_info['name'])
                        session.add(ator)
                    filme.atores.append(ator)

          
            session.add(filme)
            filmes.append(filme) 
            print(f"Processado: {titulo}")

    session.commit()
    session.close()
    return filmes  


def obter_top_filmes(session, limite=3):
    filmes = session.query(Filme).order_by(
        Filme.avaliacao.desc()).limit(limite).all()
    return filmes


def obter_url_poster(poster_path):
    base_url = 'https://image.tmdb.org/t/p/w500' 
    return f"{base_url}{poster_path}"


def obter_top_filme_por_genero(session, genero):
    filme = (
        session.query(Filme)
        .filter(Filme.generos.like(f'%{genero}%'))
        .order_by(Filme.avaliacao.desc())
        .first()
    )
    return filme


def analisar_dados():
    import pandas as pd
    import plotly.express as px
    import plotly.io as pio
    import webbrowser
    import os

    session = SessionLocal()
    filmes = session.query(Filme).all()

    
    data = {
        'Título': [f.titulo for f in filmes],
        'Avaliação': [f.avaliacao for f in filmes],
        'Data de Lançamento': [f.data_lancamento for f in filmes],
        'Gêneros': [f.generos for f in filmes],
        'Diretor': [f.diretor.nome if f.diretor else None for f in filmes],
        'Poster': [f.poster_path for f in filmes],
        'Orçamento': [f.budget for f in filmes],
        'Receita': [f.revenue for f in filmes]
    }
    df = pd.DataFrame(data)

   
    generos_unicos = set()
    for lista_generos in df['Gêneros'].str.split(', '):
        if lista_generos:
            generos_unicos.update(lista_generos)
    generos_unicos = list(generos_unicos)

    
    generos_expandidos = df['Gêneros'].str.get_dummies(sep=', ')
    genero_counts = generos_expandidos.sum().sort_values(ascending=False).reset_index()
    genero_counts.columns = ['Gênero', 'Quantidade']

   
    fig = px.bar(
        genero_counts,
        x='Gênero',
        y='Quantidade',
        title='Quantidade de Filmes por Gênero',
        template='plotly_dark'
    )

    
    fig.update_layout(
        width=800,
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        font=dict(
            family='Arial',
            size=14,
            color='white'
        ),
        xaxis_title='Gênero',
        yaxis_title='Quantidade'
    )

    
    grafico_html = pio.to_html(fig, include_plotlyjs=False, full_html=False)
    print("Gráfico de quantidade de filmes por gênero criado.")

  
    grafico_centralizado_html = f"""
    <div style="display: flex; justify-content: center;">
        {grafico_html}
    </div>
    """

   
    top_filmes = obter_top_filmes(session, limite=3)
    print("Top 3 filmes mais bem avaliados obtidos.")

    
    imagens_html = ''
    for filme in top_filmes:
        poster_url = obter_url_poster(filme.poster_path)
        imagens_html += f"""
        <div style="display: inline-block; margin: 10px; text-align: center;">
            <img src="{poster_url}" alt="{filme.titulo}" style="width:200px; height:auto;">
            <h3 style="color:white;">{filme.titulo} ({filme.avaliacao})</h3>
        </div>
        """

  
    top_filmes_por_genero = {}

    for genero in generos_unicos:
        top_filmes_gen = (
            session.query(Filme)
            .filter(Filme.generos.like(f'%{genero}%'))
            .order_by(Filme.avaliacao.desc())
            .limit(10)
            .all()
        )
        top_filmes_por_genero[genero] = top_filmes_gen
        print(f"Top 10 filmes para o gênero: {genero} obtidos.")

   
    filmes_genero_html = ''

    for genero, filmes_gen in top_filmes_por_genero.items():
        filmes_genero_html += f'<h3 style="text-align:center; margin-top:40px;">{genero}</h3>'
        filmes_genero_html += '<div style="display:flex; flex-wrap: wrap; justify-content: center;">'
        for filme in filmes_gen:
            poster_url = obter_url_poster(filme.poster_path)
            filmes_genero_html += f"""
            <div style="margin: 10px; text-align: center; width: 150px;">
                <img src="{poster_url}" alt="{filme.titulo}" style="width:100%; height:auto;">
                <p style="color:white; font-size:14px;">{filme.titulo} ({filme.avaliacao})</p>
            </div>
            """
        filmes_genero_html += '</div>'

    
    avaliacao_media_genero = (
        generos_expandidos.mul(df['Avaliação'], axis=0).sum() / generos_expandidos.sum()
    ).sort_values(ascending=False).reset_index()
    avaliacao_media_genero.columns = ['Gênero', 'Avaliação Média']
    print("Avaliação média por gênero calculada:")
    print(avaliacao_media_genero)

  
    fig_avaliacao_genero = px.bar(
        avaliacao_media_genero,
        x='Avaliação Média',
        y='Gênero',
        orientation='h',
        title='Avaliação Média por Gênero',
        template='plotly_dark'
    )


    fig_avaliacao_genero.update_layout(
        width=800,
        height=600,
        margin=dict(l=100, r=50, t=50, b=50),
        font=dict(
            family='Arial',
            size=14,
            color='white'
        ),
        xaxis_title='Avaliação Média',
        yaxis_title='Gênero'
    )


    grafico_avaliacao_genero_html = pio.to_html(fig_avaliacao_genero, include_plotlyjs=False, full_html=False)
    print("Gráfico de avaliação média por gênero criado.")


    relacao_orcamento_avaliacao_html = analisar_relacao_orcamento_avaliacao()

   
    probabilidade_lucro_html = analisar_probabilidade_lucro_por_genero()


    html_content = f"""
    <html>
    <head>
        <title>Análise de Filmes</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body style="background-color:#111; color:white; font-family: Arial, sans-serif;">
        <h1 style="text-align:center;">Análise dos Melhores Filmes</h1>
        <h2 style="text-align:center; margin-top:40px;">Top 3 Filmes Mais Bem Avaliados</h2>
        <div style="display: flex; justify-content: center;">
            {imagens_html}
        </div>
        <h2 style="text-align:center; margin-top:40px;">Quantidade de Filmes por Gênero</h2>
        {grafico_centralizado_html}
        <h2 style="text-align:center; margin-top:40px;">Avaliação Média por Gênero</h2>
        <div style="display: flex; justify-content: center;">
            {grafico_avaliacao_genero_html}
        </div>
        <h2 style="text-align:center; margin-top:40px;">Relação entre Orçamento e Avaliação Média</h2>
        <div style="display: flex; justify-content: center;">
            {relacao_orcamento_avaliacao_html}
        </div>
        <h2 style="text-align:center; margin-top:40px;">Probabilidade de Lucro por Gênero</h2>
        <div style="display: flex; justify-content: center;">
            {probabilidade_lucro_html}
        </div>
        <h2 style="text-align:center; margin-top:40px;">Filmes Mais Bem Avaliados por Gênero</h2>
        {filmes_genero_html}
    </body>
    </html>
    """
    print("Conteúdo HTML preparado.")


    with open('analise_filmes.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Análise concluída.")
    webbrowser.open('analise_filmes.html')
    session.close()









def analisar_relacao_orcamento_avaliacao():
    import pandas as pd
    import plotly.express as px
    import plotly.io as pio

    session = SessionLocal()
    filmes = session.query(Filme).all()

   
    filmes_filtrados = [f for f in filmes if f.budget and f.budget > 0 and f.avaliacao]
    if not filmes_filtrados:
        print("Nenhum filme com dados válidos de orçamento e avaliação encontrado.")
        session.close()
        return None


    data = {
        'Título': [f.titulo for f in filmes_filtrados],
        'Orçamento (em milhões)': [f.budget / 1e6 for f in filmes_filtrados],
        'Avaliação Média': [f.avaliacao for f in filmes_filtrados],
    }
    df = pd.DataFrame(data)

   
    fig = px.scatter(
        df,
        x='Orçamento (em milhões)',
        y='Avaliação Média',
        hover_name='Título',
        title='Relação entre Orçamento e Avaliação Média',
        template='plotly_dark',
    )

   
    fig.update_layout(
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_title='Orçamento (em milhões)',
        yaxis_title='Avaliação Média',
    )

   
    grafico_html = pio.to_html(fig, include_plotlyjs=False, full_html=False)
    session.close()
    return grafico_html







def analisar_probabilidade_lucro_por_genero():
    import pandas as pd
    import plotly.express as px
    import plotly.io as pio

    session = SessionLocal()
    filmes = session.query(Filme).all()

  
    filmes_validos = [f for f in filmes if f.budget and f.budget > 0 and f.revenue and f.revenue > 0]
    if not filmes_validos:
        print("Nenhum filme com dados válidos de orçamento e receita encontrado.")
        session.close()
        return None

   
    data = {
        'Gêneros': [f.generos for f in filmes_validos],
        'Lucrativo': [f.revenue > f.budget for f in filmes_validos]
    }
    df = pd.DataFrame(data)


    generos_expandidos = df['Gêneros'].str.get_dummies(sep=', ')
    lucro_por_genero = generos_expandidos.mul(df['Lucrativo'], axis=0).sum() / generos_expandidos.sum()
    total_filmes_por_genero = generos_expandidos.sum()

   
    lucro_por_genero = (lucro_por_genero * 100).sort_values(ascending=False).reset_index()
    lucro_por_genero.columns = ['Gênero', 'Probabilidade de Lucro (%)']
    lucro_por_genero['Total de Filmes'] = total_filmes_por_genero.loc[lucro_por_genero['Gênero']].values

    print("Probabilidade de lucro por gênero calculada:")
    print(lucro_por_genero)

  
    fig = px.bar(
        lucro_por_genero,
        x='Gênero',
        y='Probabilidade de Lucro (%)',
        text='Total de Filmes',  
        title='Probabilidade de Lucro por Gênero (em %)',
        template='plotly_dark'
    )


    fig.update_layout(
        width=800,
        height=500,
        margin=dict(l=50, r=50, t=50, b=50),
        font=dict(
            family='Arial',
            size=14,
            color='white'
        ),
        xaxis_title='Gênero',
        yaxis_title='Probabilidade de Lucro (%)',
        yaxis=dict(ticksuffix='%'),  
    )


    fig.update_traces(
        textposition='outside'
    )

    grafico_html = pio.to_html(fig, include_plotlyjs=False, full_html=False)
    session.close()
    return grafico_html









if __name__ == "__main__":
 
    api_key = 'eb6c19d311c8bb56c21a04bde42644bc'

    api = TMDbAPI(api_key=api_key)

    criar_banco()
    obter_dados_filmes(api, total_paginas=20)
    analisar_dados()
    analisar_relacao_orcamento_avaliacao()
    analisar_probabilidade_lucro_por_genero()

