# 🚗 GiroCar ERP

![Status do Projeto](https://img.shields.io/badge/Status-Em%20Desenvolvimento-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Interface-red)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-47c363)

## 📌 Sobre o Projeto
O **GiroCar ERP** é um sistema de Gestão Integrada desenvolvido como solução prática para concessionárias e revendas de veículos. O projeto foi construído para a disciplina de **Gestão e Qualidade de Software (GQS)** do curso de Análise e Desenvolvimento de Sistemas, sob orientação do professor Daniel Henrique Matos de Paiva.

O sistema atende aos **Objetivos de Desenvolvimento Sustentável (ODS)**, especificamente o ODS 12 (Consumo e Produção Responsáveis), ao otimizar o ciclo de vida e a revenda de veículos seminovos, reduzindo o desperdício logístico e garantindo a manutenção preventiva da frota.

## ⚙️ Tecnologias Utilizadas
- **Linguagem:** Python
- **Front-end / Interface:** Streamlit
- **Back-end / Banco de Dados:** Supabase (PostgreSQL - 3ª Forma Normal)
- **Integração Externa:** API da Tabela FIPE (via biblioteca `requests`)
- **Versionamento:** Git e GitHub
- **Deploy / CI-CD:** Streamlit Community Cloud

## 🚀 Módulos do Sistema (CRUD Completo)
1. **Dashboard Gerencial:** KPIs em tempo real, cálculo dinâmico de capital investido, gráficos de lucratividade e status do estoque.
2. **Gestão de Frota (Veículos):** Controle de entrada, filtros de busca avançados, integração de avaliação FIPE e atualização de status logístico.
3. **Comercial e Vendas:** Registro de transações, vinculação de pagamentos (PIX, Financiamento, etc) e RN01 (bloqueio de venda de carros em manutenção).
4. **Oficina e Manutenções:** Lançamento de ordens de serviço (OS) e histórico de custos.
5. **Administração e Parceiros:** Gestão de Lojas, Funcionários, Clientes e Fornecedores.

## 🛡️ Boas Práticas de Engenharia de Software (GQS)
Este repositório foi desenvolvido seguindo rigorosamente os padrões de qualidade:
- **Clean Code:** Nomenclatura padronizada, formatação de moeda local (pt-BR), interface corporativa e separação de responsabilidades.
- **Tratamento de Erros:** Uso extensivo de blocos `Try/Catch` para operações de banco de dados e APIs externas, prevenindo crashes na aplicação.
- **Git Flow & Commits Semânticos:** Uso estruturado de branches (`main`, `develop`, `feature/`, `stage`) e padronização de commits (`feat:`, `fix:`, `style:`, `docs:`, `refactor:`).
- **Testes Unitários (TDD):** Implementação de testes automatizados para as regras de negócio de faturamento.
- **Integração e Entrega Contínuas (CI/CD):** Deploy automatizado conectado diretamente à branch `main` via Streamlit Cloud.

## 🔧 Como executar o projeto localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/IcaroFeroliv/GiroCarERP
   cd GiroCarERP
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   # No Windows:
   .\venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install streamlit supabase pandas requests
   ```

4. **Configure as credenciais do banco:**
   Crie uma pasta oculta chamada `.streamlit` na raiz do projeto e um arquivo `secrets.toml` dentro dela com as chaves do seu Supabase:
   ```toml
   SUPABASE_URL = "sua_url_aqui"
   SUPABASE_KEY = "sua_chave_anon_aqui"
   ```

5. **Rode a aplicação:**
   ```bash
   streamlit run 00_Dashboard.py
   ```

## 👥 Equipe de Desenvolvimento
- **Ícaro**: Arquitetura, Banco de Dados, Dashboard e Módulo de Veículos.
- **Kaio**: Interface Visual (UI/UX) e Módulos de Parceiros/Administração.
- **Erick**: Regras de Negócio Financeiras, Módulo Comercial, Oficina e Testes Unitários.

---
*Projeto acadêmico desenvolvido em Outubro de 2026 para composição da nota da Avaliação A3.*