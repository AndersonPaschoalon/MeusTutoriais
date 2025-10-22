# 🧭 **Git Intermediário na Prática — Do Dia a Dia Profissional ao Controle Total**

> Um guia sob medida para quem já domina o básico e quer parar de brigar com o Git.

---

## 📍 Sumário

1. **Relembrando o essencial (sem enrolar)**
2. **Sincronização e atualização segura com `origin`**
3. **Branches e merges inteligentes (sem perder o que já fez)**
4. **Gerenciamento de tags e versões**
5. **Stash e reversões seguras**
6. **Inspeção e comparações (diffs, logs e blame)**
7. **Correção de commits e limpeza de histórico**
8. **Resolução de conflitos como um adulto**
9. **Gitignore avançado (escopos e exceções)**
10. **Dicas extras: produtividade e sanity checks**

---

## ⚙️ 1. Relembrando o essencial (sem enrolar)

Você já sabe o básico:

```bash
git add .
git commit -m "mensagem"
git push
```

Mas, o Git **não é um “salvar arquivo”**, é uma *máquina de tempo distribuída*.
Seu poder está em **controlar versões com segurança** e **sincronizar sem medo de perder código**.

---

## 🔄 2. Sincronização e atualização segura com `origin`

### 🧠 Cenário comum:

Você está desenvolvendo em um branch desatualizado e quer sincronizar com `develop`, **sem perder seu trabalho local ainda instável**.

### ✅ Solução segura:

```bash
# Garante que você está no seu branch
git status
git branch

# Atualiza referências do remoto
git fetch origin

# Faz merge das mudanças do develop no seu branch atual
git merge origin/develop
```

💡 *Dica:* se você quer ver o que virá **antes de mergear**:

```bash
git diff HEAD..origin/develop --stat
```

---

## 🌿 3. Branches e merges inteligentes

### Criar branch a partir de develop:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/awesome-feature
```

### Atualizar seu branch com develop:

```bash
git fetch origin
git merge origin/develop
```

### Resolver conflitos visualmente:

```bash
git mergetool
```

👉 Configure o VSCode como ferramenta padrão:

```bash
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd "code --wait $MERGED"
```

---

## 🏷️ 4. Gerenciamento de tags e versões

Tags marcam pontos importantes (releases, deploys, etc.).

### Criar e enviar:

```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

### Atualizar uma tag (mudou o release)

```bash
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
git tag -a v1.0.0 -m "Updated release"
git push origin v1.0.0
```

### Sincronizar tags (atualizar e limpar):

```bash
git fetch origin --tags --prune
```

---

## 🪣 5. Stash e reversões seguras

### Guardar alterações não commitadas:

```bash
git stash push -m "backup before deploy"
```

### Listar e restaurar:

```bash
git stash list
git stash apply stash@{0}
```

### Reverter ao estado anterior ao commit:

```bash
git reset --soft HEAD^    # mantém alterações
git reset --hard HEAD^    # descarta tudo
```

💡 *Voltar dois commits:*

```bash
git reset --soft HEAD~2
```

---

## 🔍 6. Inspeção e comparação

### Ver o que mudou entre duas tags:

```bash
git diff v0.13 v0.14 -- path/to/file.py
```

### Ver commits entre versões:

```bash
git log v0.13..v0.14 --oneline --decorate
```

### Ver quem mexeu em uma linha específica:

```bash
git blame services/update/inventory_updater.py
```

---

## 🧹 7. Corrigir commits e limpar histórico

### Desfazer último commit mas manter alterações:

```bash
git reset --soft HEAD^
```

### Remover arquivo grande que foi commitado por engano:

```bash
git rm --cached path/to/large_file.bin
git commit --amend
git push origin branch --force
```

> ⚠️ Use `--force` apenas se for **seu branch pessoal** (ou avisar o time antes).

---

## ⚔️ 8. Resolução de conflitos profissional

1. Após um `merge` ou `rebase`, se houver conflitos:

   ```bash
   git status
   ```

   → veja quais arquivos estão com `<<<<<<< HEAD`.

2. Corrija manualmente (ou via VSCode):

   ```bash
   git mergetool
   ```

3. Depois de resolver:

   ```bash
   git add .
   git merge --continue
   ```

---

## 🧩 9. Gitignore avançado (escopos e exceções)

Exemplo de caso seu (ignorar `.dll` globalmente, mas versionar em uma pasta específica):

`.gitignore` global:

```gitignore
*.dll
```

Exceção em subpasta (`subproject/.gitignore`):

```gitignore
!libs/**/*.dll
```

💡 “!” significa **não ignore isso**, mesmo que a regra global diga o contrário.

---

## ⚡ 10. Dicas extras

### Limpar branches locais que já foram deletados no remoto:

```bash
git fetch -p
git branch -vv | grep ': gone' | awk '{print $1}' | xargs git branch -d
```

### Ver commits e merges de forma gráfica:

```bash
git log --oneline --graph --decorate --all
```

### Atualizar produção com segurança:

```bash
git stash push -m "backup pre-release"
git fetch origin --tags
git checkout v0.28.3
```

Para reverter:

```bash
git stash pop
```

---

## 🧭 Conclusão

Esse guia cobre exatamente o ponto entre o *Git básico* e o *uso profissional diário*, com ênfase em:

* Segurança (sem perda de código)
* Controle de tags e releases
* Comparação entre versões
* Correção e limpeza sem traumas
* Resolução de conflitos sem pânico

---

Posso gerar esse tutorial em **PDF formatado com seções e realce de código** para você guardar localmente (tipo um mini e-book profissional).
Quer que eu gere agora?
