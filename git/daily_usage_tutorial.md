## 🚀 Daily Professional Git Workflow

### ✅ 1. Sync With Origin (The Right Way)

**Before starting anything, always update your local branches:**

```bash
git checkout develop                # Or the main working branch
git pull origin develop             # Pull latest changes
git fetch --all --prune             # Fetch all branches and remove stale ones
```

> Why? Keeps your local repo up-to-date and clean.

---

### 🌿 2. Creating and Managing Feature Branches

**Start new work by branching from the latest stable base:**

```bash
git checkout develop                # Ensure you're on the right base
git pull origin develop             # Update it
git checkout -b feature/your_task  # Create and switch to a new branch
```

> Do NOT work directly on `develop` or `main`. Isolate all tasks into a branch.

---

### 🛠 3. Making Commits

**Stage and commit changes properly:**

```bash
git status                          # Check current changes
git add .                           # Stage all changes (or choose specific files)
git commit -m "feat: add login validation"
```

> Use conventional commit messages: `feat`, `fix`, `chore`, `refactor`, etc.

---

### 🔁 4. Syncing Your Branch with Develop (Avoiding Big Conflicts)

> Merge = safer in teams. Use according to your team's preference.
> Rebase = cleaner history.

* Merge:
```bash
git merge origin/develop
```

* Rebase:
```bash
git fetch origin
git rebase origin/develop
```

---

### 🤝 5. Creating a Merge Request (MR) / Pull Request (PR)

**Push your branch and create a PR via Git platform:**

```bash
git push -u origin feature/your_task
```

Then go to GitHub/GitLab to open a merge request.

---

### 🔧 6. Resolving Merge Conflicts

If there are conflicts:

```bash
git status                        # See conflicting files
# Open files and resolve conflicts manually
git add conflicted_file.py       # Mark as resolved
git commit                       # Finalize merge
```

> If using `rebase`, use `git rebase --continue`.

---

### 💡 7. Cleaning Up

**After your branch is merged:**

```bash
git checkout develop
git pull origin develop
git branch -d feature/your_task     # Delete local
git push origin --delete feature/your_task  # Delete remote (if allowed)
```

---

## 🧰 Common Useful Commands

| Command                           | Purpose                                |
| --------------------------------- | -------------------------------------- |
| `git log --oneline --graph --all` | Visualize branch history               |
| `git stash` / `git stash pop`     | Temporarily save/restore local changes |
| `git cherry-pick <commit>`        | Copy a specific commit                 |
| `git diff`                        | Show unstaged changes                  |
| `git reset --hard HEAD`           | Reset everything (DANGEROUS)           |
| `git reflog`                      | Recover lost commits or branches       |
| `git clean -fd`                   | Remove untracked files/directories     |
| `git remote -v`                   | Show remote URLs                       |
| `git branch -vv`                  | Show all branches and upstreams        |

---

Would you like this tutorial saved as a PDF, cheat sheet, or added as a Markdown to your repo?
