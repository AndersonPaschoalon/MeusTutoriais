## **Guia Completo: Desvendando o sites-enabled do Nginx**

O Nginx é um dos servidores web e proxies reversos mais populares do mundo, conhecido por sua alta performance e baixo consumo de recursos. Uma de suas características mais poderosas e, às vezes, confusas para iniciantes, é a forma como ele gerencia as configurações de diferentes sites através dos diretórios /etc/nginx/sites-available e /etc/nginx/sites-enabled.  
Este guia vai desmistificar esse conceito e detalhar a estrutura de um arquivo de configuração de site, capacitando você a hospedar múltiplos sites e aplicações em um único servidor.

### **O Paradigma: sites-available vs. sites-enabled**

A primeira coisa a entender é que você **não edita arquivos diretamente** no diretório sites-enabled. Este diretório contém apenas **atalhos (links simbólicos)** para os arquivos de configuração reais, que ficam em sites-available.

* **/etc/nginx/sites-available/**: Este é o seu "depósito" de configurações. Cada arquivo aqui representa a configuração completa de um site ou aplicação que você *pode* querer ativar. Você pode ter dezenas de arquivos aqui, um para cada projeto.  
* **/etc/nginx/sites-enabled/**: Este é o diretório que o Nginx realmente lê ao iniciar. Ele contém apenas os atalhos para os arquivos em sites-available que você quer que estejam **ativos** no momento.

Por que essa separação?  
Essa arquitetura genial permite que você ative e desative sites de forma rápida e segura, sem precisar apagar ou renomear arquivos de configuração.

* **Para ativar um site:** Você cria um link simbólico do arquivo em sites-available para sites-enabled.  
* **Para desativar um site:** Você simplesmente apaga o link simbólico em sites-enabled. O arquivo de configuração original permanece intacto em sites-available, pronto para ser reativado no futuro.

### **A Anatomia de um Arquivo de Configuração (O Bloco server)**

Cada arquivo em sites-available define um ou mais "blocos server". Cada bloco server funciona como um "host virtual", definindo como o Nginx deve responder a requisições para um domínio específico.  
Vamos analisar um exemplo bem comentado de um arquivo de configuração, que poderia se chamar /etc/nginx/sites-available/meuprojeto.com.  
\# Este é um bloco de servidor. Ele define as configurações para um site específico.  
server {  
    \# \--- Diretivas de Escuta (Listen) \---  
    \# O Nginx escutará na porta 80 (HTTP padrão) para todas as interfaces de rede IPv4 e IPv6.  
    listen 80;  
    listen \[::\]:80;

    \# \--- Nomes do Servidor (Server Name) \---  
    \# Esta diretiva informa ao Nginx para qual(is) domínio(s) este bloco deve responder.  
    \# Ele responde a "meuprojeto.com" e ao seu subdomínio "www".  
    server\_name meuprojeto.com www.meuprojeto.com;

    \# \--- Raiz dos Documentos (Document Root) \---  
    \# O diretório no servidor onde os arquivos do site estão localizados.  
    root /var/www/meuprojeto.com/html;

    \# \--- Arquivo de Índice (Index File) \---  
    \# Se uma requisição for para um diretório (ex: "/"), o Nginx tentará servir  
    \# estes arquivos, nesta ordem.  
    index index.html index.htm;

    \# \--- Blocos de Localização (Location Blocks) \---  
    \# Esta é a parte mais poderosa. Ela define como tratar requisições para diferentes URIs.

    \# Bloco de localização para a raiz ("/").  
    \# Toda requisição que não corresponder a outro bloco mais específico cairá aqui.  
    location / {  
        \# Tenta servir o arquivo exato solicitado ($uri).  
        \# Se não encontrar, tenta servir um diretório com esse nome ($uri/).  
        \# Se falhar, retorna um erro 404\.  
        \# Essencial para sites estáticos.  
        try\_files $uri $uri/ \=404;  
    }

    \# Bloco de localização para uma API (ex: /api/users).  
    \# Este é um exemplo de proxy reverso.  
    location /api/ {  
        \# Remove o prefixo /api/ da URL antes de enviar para o backend.  
        \# Ex: /api/users \-\> /users  
        rewrite ^/api/(.\*)$ /$1 break;

        \# Passa a requisição para uma aplicação backend rodando localmente na porta 8000  
        \# (poderia ser uma aplicação FastAPI, Node.js, etc.).  
        proxy\_pass http://127.0.0.1:8000;

        \# Define cabeçalhos importantes para que a aplicação backend saiba  
        \# informações sobre a requisição original.  
        proxy\_set\_header Host $host;  
        proxy\_set\_header X-Real-IP $remote\_addr;  
        proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for;  
        proxy\_set\_header X-Forwarded-Proto $scheme;  
    }

    \# \--- Configurações de Log (Opcional, mas recomendado) \---  
    \# Caminho para o log de acessos deste site específico.  
    access\_log /var/log/nginx/meuprojeto.com.access.log;  
    \# Caminho para o log de erros deste site.  
    error\_log /var/log/nginx/meuprojeto.com.error.log;  
}

### **Gerenciando as Configurações: Passo a Passo**

Agora que entendemos a estrutura, vamos ao processo prático.  
1\. Crie o Arquivo de Configuração  
Use um editor de texto como o nano para criar seu arquivo em sites-available.  
sudo nano /etc/nginx/sites-available/meuprojeto.com

Cole o conteúdo do seu bloco server (como o exemplo acima) e salve o arquivo.  
2\. Ative o Site (Crie o Link Simbólico)  
Agora, crie o "atalho" em sites-enabled que aponta para o seu novo arquivo.  
sudo ln \-s /etc/nginx/sites-available/meuprojeto.com /etc/nginx/sites-enabled/

*ln \-s* é o comando para criar um link simbólico.  
3\. Teste a Configuração do Nginx  
Antes de aplicar as mudanças, é crucial verificar se não há erros de sintaxe no seu arquivo.  
sudo nginx \-t

Se tudo estiver correto, você verá uma mensagem como:  
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok  
nginx: configuration file /etc/nginx/nginx.conf test is successful

Se houver um erro, o Nginx informará o arquivo e a linha onde o problema está.  
4\. Aplique as Mudanças  
Se o teste passou, recarregue o Nginx para aplicar a nova configuração sem derrubar as conexões existentes.  
sudo systemctl reload nginx

Seu novo site agora está ativo\!  
5\. Desative um Site  
Para desativar o site, basta remover o link simbólico.  
sudo rm /etc/nginx/sites-enabled/meuprojeto.com

Depois, recarregue o Nginx para que a mudança tenha efeito:  
sudo systemctl reload nginx

### **Um Toque sobre HTTPS (SSL/TLS)**

Para habilitar HTTPS, seu bloco server precisará de algumas diretivas adicionais. Geralmente, você cria um segundo bloco server ou modifica o existente para escutar na porta 443\.  
Um bloco HTTPS básico se parece com isto:  
server {  
    listen 443 ssl http2;  
    listen \[::\]:443 ssl http2;  
    server\_name meuprojeto.com www.meuprojeto.com;

    \# Caminho para seus certificados SSL  
    ssl\_certificate /etc/letsencrypt/live/meuprojeto.com/fullchain.pem;  
    ssl\_certificate\_key /etc/letsencrypt/live/meuprojeto.com/privkey.pem;

    \# ... resto da sua configuração (root, location, etc.) ...  
}

A maneira mais fácil de obter e configurar certificados SSL hoje em dia é usando a ferramenta **Certbot**, que automatiza a obtenção de certificados gratuitos da Let's Encrypt e pode até mesmo configurar seus arquivos Nginx para você.

### **Conclusão**

Dominar a estrutura sites-available/sites-enabled e a sintaxe dos blocos server é o passo mais importante para se tornar proficiente com o Nginx. Essa abordagem modular permite gerenciar dezenas de sites de forma limpa, organizada e segura, tornando a administração do seu servidor uma tarefa muito mais simples.