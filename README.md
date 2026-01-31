🏦 FinBot: Assistente Virtual com IA Generativa para Finanças
O FinBot é uma solução de inteligência artificial voltada para o setor bancário que une a precisão de algoritmos financeiros com a flexibilidade da IA Generativa. O projeto foi desenvolvido para oferecer uma experiência de autoatendimento fluida, educativa e segura.

🎯 Objetivo
Resolver a lacuna entre a complexidade do mercado financeiro e o entendimento do usuário final, utilizando Processamento de Linguagem Natural (PLN) para fornecer suporte, simulações e educação financeira em tempo real.

🚀 Funcionalidades Principais
💳 Consulta de Saldo e Limites: Acesso rápido a dados financeiros com formatação monetária padrão (BRL).

📊 Simulador de Empréstimos: Motor de cálculo que valida solicitações contra limites pré-aprovados e projeta parcelas com juros.

📚 FAQ Inteligente: Explicação de produtos financeiros (CDB, LCI, PIX) em linguagem acessível.

🧠 Memória de Contexto: Capacidade de manter o histórico da conversa para respostas personalizadas durante a sessão.

🤖 IA Híbrida: Uso de lógica determinística para números e generativa para interação humana.

🛠️ Tecnologias Utilizadas
Python 3.x: Linguagem base para toda a lógica de backend.

Lógica de Dicionários (Hash Maps): Para simulação eficiente de banco de dados e mapeamento de intenções.

NLU (Natural Language Understanding): Implementação de lógica de detecção de intenção por palavras-chave e contexto.

UX Design: Aplicação de princípios de tom de voz, tempos de resposta humanizados e tratamento de erros amigável.

📂 Estrutura do Projeto
main.py: Ponto de entrada da aplicação e interface de linha de comando.

finbot_engine.py: Motor lógico contendo as classes de simulação e processamento de texto.

database_mock.py: Simulação de estrutura de dados de clientes e produtos.

🧠 Como Funciona (Arquitetura)
O fluxo de interação segue três camadas:

Entrada do Usuário: Captura do texto via console ou interface.

Roteador de Intenção: O Python identifica se o usuário quer um Cálculo (Saldo/Simulação) ou uma Explicação (Educação Financeira).

Saída Humanizada: A resposta é formatada com regras de UX para garantir clareza e empatia.

📝 Exemplo de Uso
Usuário: "O que é um CDB e quanto eu tenho na conta?"

FinBot: "O CDB é um investimento onde você empresta dinheiro ao banco... Sobre sua conta, seu saldo atual é de R$ 4.500,00. Posso te ajudar a investir parte disso?"

🌟 Diferenciais de UX aplicados
Prevenção de Erros: O sistema valida valores antes de processar cálculos.

Visibilidade do Sistema: Mensagens de "processando" e "digitando" reduzem a ansiedade do usuário.

Estética e Minimalismo: Informações apresentadas de forma organizada com uso de Markdown para destaque.
