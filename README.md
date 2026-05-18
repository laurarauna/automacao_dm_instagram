# Automação de DM no Instagram

Este repositório contém o código-fonte de uma automação *Server-to-Server* desenvolvida para a conta comercial do Instagram **@casa__curadoria**. O objetivo da aplicação é converter o engajamento público (comentários) em interações privadas e conversões, enviando links de produtos (ex: afiliados Shopee) automaticamente via Direct Message (DM) quando um seguidor comenta uma palavra-chave específica.

Construção de pipeline de ingestão de dados em tempo real consumindo a Meta Graph API. Arquitetura Server-to-Server com deploy em nuvem (Render).

## ⚙️ Arquitetura e Tecnologias

O projeto foi construído sem interface gráfica (*Front-end*), rodando 100% no *Back-end*, utilizando as seguintes ferramentas:

* **Hospedagem:** [Render.com](https://render.com/) (PaaS)
* **Banco de Dados/Configuração:** Google Sheets API
* **Integração:** Meta Graph API (Instagram Webhooks)
* **Linguagem/Ambiente:** Python

## 🔄 Fluxo de Funcionamento (Como funciona)

O processo inteiro é automatizado e ocorre em questão de segundos:

1.  **O Gatilho (Consentimento):** A página publica um post de "achadinhos" e pede na legenda para o seguidor comentar uma palavra-chave (ex: *"QUERO"*).
2.  **O Webhook:** O usuário comenta no post. A Meta Graph API detecta a interação e dispara um evento (Webhook) contendo o *payload* do comentário para o nosso servidor hospedado no Render.
3.  **Processamento e Validação:** O servidor recebe o Webhook e verifica:
    * Se o evento ocorreu na conta correta (`instagram_business_basic`).
    * Se o texto do comentário contém a palavra de gatilho exata (`instagram_business_manage_comments`).
4.  **Consulta de Banco de Dados:** O código se conecta a uma planilha do Google Sheets. A planilha funciona como um painel de controle contendo: `Link do Post` | `Palavra-chave` | `Mensagem a ser enviada` | `Link do Produto (Shopee)`.
5.  **A Ação (Envio da DM):** Uma vez que os dados batem, o servidor faz uma requisição POST para a Meta Graph API, enviando a mensagem e o link de forma privada para a caixa de entrada do usuário (`instagram_business_manage_messages`).

## 🔐 Permissões da Meta App

Para que o robô funcione, o aplicativo no Painel de Desenvolvedor da Meta requer o nível de **Acesso Avançado** nas seguintes permissões:

* `instagram_business_basic`: Para ler os metadados do perfil e validar a origem do comentário.
* `instagram_business_manage_comments`: Para escutar passivamente os Webhooks e identificar a palavra-chave.
* `instagram_business_manage_messages`: Para executar o disparo automatizado da DM.

> **Nota sobre a revisão da Meta:** Como este é um aplicativo *Server-to-Server*, o fluxo de autenticação não utiliza telas de login (*Facebook Login*). A autorização é feita via **Tokens de Acesso de Usuário do Sistema** gerados no Gerenciador de Negócios e configurados nas variáveis de ambiente do servidor.

## 🚀 Configuração do Ambiente

Para rodar este projeto localmente ou em um novo servidor, é necessário configurar as seguintes variáveis de ambiente (`.env`):

* `VERIFY_TOKEN`: Token de segurança para validação do Webhook na Meta.
* `PAGE_ACCESS_TOKEN` ou `SYSTEM_USER_TOKEN`: Token de acesso com permissão para gerenciar a conta do Instagram vinculada.
* `GOOGLE_SHEETS_CREDENTIALS`: JSON com as credenciais da API do Google Cloud.
* `SPREADSHEET_ID`: O ID da planilha do Google usada como banco de dados.

## 📌 Observações Finais

Este projeto automatiza a entrega de valor aos seguidores, diminuindo o atrito na jornada de compra e garantindo que o usuário receba a informação solicitada de forma instantânea e segura, respeitando as políticas de privacidade e consentimento da plataforma.
