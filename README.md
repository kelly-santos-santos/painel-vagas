# Painel Automático de Candidaturas — Kelly Cristina Santos e Santos

Este pacote contém seu painel com o visual turquesa e laranja (`index.html`) conectado a uma automação gratuita no GitHub Actions que busca vagas automaticamente às **08:00, 10:00, 12:00, 14:00, 16:00 e 18:00** (horário de São Paulo) e atualiza o site sozinho.

## Como publicar e ligar ao seu Google Sites
1. Crie uma conta gratuita no **GitHub** (github.com) e crie um repositório público chamado `painel-vagas`.
2. Descompacte este arquivo e suba todos os arquivos (incluindo a pasta `.github/workflows/`).
3. No repositório, vá em **Settings > Pages**, selecione **Deploy from a branch**, escolha `main` e `/ (root)`, e clique em **Save**.
4. Copie a URL gerada pelo GitHub Pages (ex.: `https://seu-usuario.github.io/painel-vagas/`).
5. No seu **Google Sites**, substitua o bloco de *Incorporar código* por **Incorporar > Por URL** e cole essa URL.
