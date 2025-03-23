import streamlit as st
import pandas as pd
import sqlite3
from faker import Faker

#Fluxo de Caixa por Mês: Gráfico de linha ou de barras mostrando a receita e despesa ao longo dos meses
#Top 5 Clientes com Maior Receita: Tabela e gráfico de barras mostrando os clientes que mais geram receita
#Status das Contas a Pagar e Receber: Gráfico de barras mostrando o total de contas "Pendentes" vs "Pagas/Recebidas"

# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    
    menu = [
        "Clientes", 
        "Contas a Pagar", 
        "Contas a Receber", 
        "Lançamentos", 
        "Relatórios",
        "Fluxo de Caixa por Mês",
        "Top 5 Clientes com Maior Receita",
        "Status das Contas a Pagar e Receber"]
    
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
        
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
        
    elif choice == "Relatórios":
        st.subheader("Relatório de Fluxo de Caixa")
        df = pd.read_sql_query("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo", conn)
        st.dataframe(df)

    elif choice == "Fluxo de Caixa por Mês":
        st.subheader("Fluxo de Caixa por Mês")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)

        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df['day'] = df['data'].dt.date

        grouped = df.groupby(['day', 'tipo'])['valor'].sum().reset_index()
        pivot_df = grouped.pivot(index='day', columns='tipo', values='valor').fillna(0)

        st.line_chart(pivot_df)

    elif choice == "Top 5 Clientes com Maior Receita":
        st.subheader("Top 5 Clientes com Maior Receita")
        query = """
        SELECT c.nome AS cliente,
               SUM(cr.valor) as total_receita
        FROM contas_receber cr
        JOIN clientes c ON cr.cliente_id = c.id
        WHERE cr.status = 'Recebido'
        GROUP BY c.id
        ORDER BY total_receita DESC
        LIMIT 5
        """
        df = pd.read_sql_query(query, conn)

        st.dataframe(df)

        df_chart = df.set_index("cliente")

        st.bar_chart(df_chart["total_receita"])

    elif choice == "Status das Contas a Pagar e Receber":
        st.subheader("Status das Contas a Pagar e a Receber")

        df_pagar = pd.read_sql_query("""
            SELECT status, COUNT(*) as total
            FROM contas_pagar
            GROUP BY status
        """, conn)
        df_pagar["tipo_conta"] = "Pagar"

        df_receber = pd.read_sql_query("""
            SELECT status, COUNT(*) as total
            FROM contas_receber
            GROUP BY status
        """, conn)
        df_receber["tipo_conta"] = "Receber"

        df_status = pd.concat([df_pagar, df_receber], ignore_index=True)
        df_status.loc[df_status['status'].isin(['Pago', 'Recebido']), 'status'] = 'Concluída'
        pivot_df = df_status.pivot(index='tipo_conta', columns='status', values='total').fillna(0)

        st.write("Gráfico de Barras - Contas Pendentes vs Concluídas")
        st.bar_chart(pivot_df)

    conn.close()
    
if __name__ == "__main__":
    main()
