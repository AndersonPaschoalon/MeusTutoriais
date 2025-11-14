# **Capítulo 7 — Comunicação Interprocessos (IPC)**

*“Se processos são como pequenas ilhas computacionais, o IPC é a ponte que permite que elas cooperem.” – em estilo Andrew S. Tanenbaum*

---

## **7.1 Conceito e importância do IPC**

A execução concorrente de processos e tarefas é inútil se não houver meios de coordenação entre eles. Em um sistema multitarefa, cada processo possui seu próprio espaço de endereçamento ou, no mínimo, seu próprio contexto de execução. Essa separação é essencial para a robustez do sistema, mas cria um novo problema: **como dois processos trocam informações de forma segura e ordenada?**

Esse problema é resolvido pelos mecanismos de **IPC — Interprocess Communication**. Eles permitem que tarefas cooprem, sincronizem o uso de recursos e troquem dados. O IPC é especialmente importante em sistemas embarcados e de tempo real, onde **determinismo** e **baixa latência** são requisitos fundamentais.

Existem essencialmente duas grandes categorias:

1. **IPC baseado em sincronização**
   usados para coordenar acesso a recursos (semáforos, mutexes, eventos).

2. **IPC baseado em troca de dados**
   usados para enviar informações (filas, mailboxes, pipes).

Um bom sistema operacional oferece ambos.

Para tornar o conceito mais tangível, observe que até operações simples — como impedir que duas tarefas escrevam no mesmo buffer simultaneamente — exigem IPC.

---

## **7.2 Mecanismos básicos: semáforos, mutexes, filas, sinais**

### **Semáforos**

O semáforo é provavelmente o mecanismo de sincronização mais clássico e, sem exagero, um dos mais mal usados. Introduzido por Dijkstra nos anos 1960, um semáforo é uma variável inteira protegida por operações atômicas:

* **P()**: decrementar
* **V()**: incrementar

Em sistemas reais, essas operações podem bloquear a tarefa quando o valor é negativo (semáforo contável) ou funcionar como um simples *lock* (semáforo binário).

Um exemplo típico de semáforo binário no Linux (via POSIX):

```c
#include <semaphore.h>

sem_t sem;

void init() {
    sem_init(&sem, 0, 1); // semáforo binário inicializado como "livre"
}

void *task(void *arg) {
    sem_wait(&sem); // P()
    // seção crítica
    sem_post(&sem); // V()
    return NULL;
}
```

### **Mutexes**

Um *mutex* (MUTual EXclusion) é semelhante a um semáforo binário, mas com semântica mais restrita:

* apenas o dono do lock pode liberá-lo;
* pode ter mecanismos de prevenção de **inversão de prioridade**, como *priority inheritance*.

Em sistemas de tempo real — incluindo Linux com **PREEMPT_RT** — mutexes com herança de prioridade são essenciais.

Exemplo Linux (pthread mutex):

```c
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void *task(void *arg) {
    pthread_mutex_lock(&lock);
    // seção crítica
    pthread_mutex_unlock(&lock);
}
```

### **Filas (Message Queues)**

Filas são adequadas quando tarefas precisam trocar mensagens estruturadas. São amplamente usadas em RTOS como FreeRTOS, Zephyr e VxWorks.

Exemplo FreeRTOS:

```c
QueueHandle_t q = xQueueCreate(10, sizeof(int));
int value = 42;

xQueueSend(q, &value, portMAX_DELAY);
xQueueReceive(q, &value, portMAX_DELAY);
```

Com message queues, a sincronização está implícita: se a fila está vazia, o consumidor bloqueia; se está cheia, o produtor bloqueia.

### **Sinais** (Signals)

Em Unix/Linux, sinais servem mais para **notificação assíncrona** que para comunicação estruturada.

Exemplo simples:

```c
void handler(int sig) {
    write(1, "signal received\n", 16);
}

int main() {
    signal(SIGUSR1, handler);
    pause();
}
```

Apesar de úteis, sinais são perigosos: executam de forma assíncrona, com enorme restrição do que pode ser feito dentro do handler (similar às restrições de ISR).

---

## **7.3 Mailboxes e eventos**

### **Mailboxes**

Mailboxes são semelhantes às filas, mas normalmente aceitam **prioridade de mensagens**, ou permitem mensagens de tamanho variável. RTOS de classe industrial (p.ex., VxWorks) usam mailboxes para comunicação entre tarefas e entre ISR e tarefas.

Estrutura típica de mailbox:

* Uma tarefa envia uma mensagem (geralmente ponteiro).
* Outra tarefa *bloqueia* até receber.
* Pode haver prioridade por remetente ou por tipo de mensagem.

### **Eventos**

Eventos funcionam como “sinais binários”, usados para sincronizar tarefas baseadas em condições.

Exemplo clássico FreeRTOS — *event groups*:

```c
EventGroupHandle_t ev = xEventGroupCreate();

// Tarefa A
xEventGroupSetBits(ev, BIT_0);

// Tarefa B
xEventGroupWaitBits(ev, BIT_0, pdTRUE, pdFALSE, portMAX_DELAY);
```

Eventos são úteis quando várias tarefas aguardam uma mesma condição.

---

## **7.4 Pipes e buffers circulares**

### **Pipes**

Em Unix, um pipe conecta saída de um processo à entrada de outro. É um canal FIFO unidirecional.

```c
int fds[2];
pipe(fds);

write(fds[1], "hello", 5);
read(fds[0], buf, sizeof(buf));
```

Pipes podem ser:

* **anônimos** (pai-filho)
* **nomeados**, via *mkfifo*, permitindo comunicação entre processos independentes.

### **Buffers circulares**

São estruturas que reaproveitam um buffer linear conectando fim → início, muito úteis em drivers, ISR e sistemas embarcados.

Pseudocódigo (típico de drivers Linux):

```c
struct ring {
    char buf[256];
    int head, tail;
};

int ring_put(struct ring *r, char c) {
    int next = (r->head + 1) % sizeof(r->buf);
    if (next == r->tail) return -1; // cheio
    r->buf[r->head] = c;
    r->head = next;
    return 0;
}

int ring_get(struct ring *r, char *c) {
    if (r->head == r->tail) return -1; // vazio
    *c = r->buf[r->tail];
    r->tail = (r->tail + 1) % sizeof(r->buf);
    return 0;
}
```

Buffers circulares são extremamente determinísticos e adequados para comunicação ISR → tarefa.

---

## **7.5 Sincronização e exclusão mútua**

A exclusão mútua garante que apenas uma tarefa execute a *seção crítica* por vez.

### **Problema da Seção Crítica**

Um bom mecanismo de sincronização deve atender:

1. **Exclusão mútua**
   nunca duas tarefas na seção crítica simultaneamente.

2. **Progresso**
   tarefas fora da seção crítica não devem bloquear as dentro.

3. **Espera limitada (bounded waiting)**
   nenhuma tarefa deve esperar indefinidamente.

Além disso, em sistemas de tempo real adicionamos mais um:

4. **Determinismo**
   não apenas limitado — mas com limite conhecido.

### **Primitivas usuais**

* Mutexes
* Semáforos binários
* Spinlocks (apenas em kernel)
* Disable interrupts (apenas em seções curtíssimas)

Exemplo Linux kernel — *spinlock*:

```c
spinlock_t lock;

unsigned long flags;

spin_lock_irqsave(&lock, flags);
// seção crítica protegida contra preempção e interrupções
spin_unlock_irqrestore(&lock, flags);
```

Spinlocks são úteis apenas quando a espera é curta e o código está em contexto onde bloquear não é permitido (como dentro de ISR).

Mutexes são adequados para código de longa duração em espaço de usuário ou kernel *thread*.

---

## **7.6 Deadlocks e condições de corrida**

### **Condições de corrida**

Ocorrem quando o resultado depende da ordem de execução das tarefas. Exemplo simples:

```c
counter++; // não atômico!
```

Em assembly x86, isso poderia se decompor em:

```asm
mov eax, [counter]
inc eax
mov [counter], eax
```

Se duas tarefas executam essas instruções simultaneamente, uma atualização pode ser perdida.

Correção: usar exclusão mútua ou instruções atômicas:

```c
__sync_fetch_and_add(&counter, 1);
```

### **Deadlocks**

Ocorrem quando duas (ou mais) tarefas ficam bloqueadas esperando recursos umas das outras. O exemplo clássico:

* Tarefa A segura **mutex1** e espera por **mutex2**.
* Tarefa B segura **mutex2** e espera por **mutex1**.

Nenhuma progride.

As quatro condições para deadlock (Coffman):

1. Exclusão mútua
2. Hold and wait (segurar um recurso e esperar outro)
3. Não-preempção
4. Espera circular

Para evitar deadlocks, muitos sistemas embarcados impõem **ordenação global de locks**: todos os mutexes têm uma ordem e devem ser adquiridos sempre na mesma direção.

### **Starvation**

Uma tarefa nunca obtém recursos porque outras sempre passam na frente. É típico em sistemas com prioridades fixas ou filas não justas.

Correção comum: esquemas de justiça (*fair queues*, *aging*).

