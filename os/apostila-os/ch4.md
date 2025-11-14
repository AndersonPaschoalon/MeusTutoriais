# 📘 **Capítulo 4 — Gerenciamento de Processos e Tarefas**

Sistemas embarcados raramente executam “processos” no sentido clássico dos sistemas operacionais de desktops e servidores. Em vez disso, lidam com **tarefas**, “threads” leves e previsíveis que compartilham o mesmo espaço de endereçamento e cooperam para executar um trabalho comum.

Se um kernel de propósito geral pode ser imaginado como uma metrópole moderna — com bairros separados, ruas complexas e isolamento rígido —, um RTOS se parece muito mais com uma pequena aldeia: as tarefas vivem próximas umas das outras, compartilham recursos, e qualquer abuso pode afetar toda a comunidade.

---

## **4.1 Conceito de tarefa (*task* ou *thread*)**

Em um sistema embarcado, uma *task* é uma **unidade básica de execução**, equivalente a uma pequena função que o kernel pode interromper, pausar e retomar. Ao contrário dos processos tradicionais (com memória isolada, arquivos, espaços de endereçamento independentes), as tarefas em um RTOS:

* Compartilham o mesmo espaço de memória;
* Possuem apenas sua própria *stack*;
* São agendadas com base em **prioridades**;
* Executam porções de código bastante especializadas;
* Cooperam explícita ou implicitamente via mecanismos de IPC.

Tanenbaum provavelmente diria que, enquanto processos em desktops são como “atores independentes”, tarefas embarcadas são como “membros de uma mesma equipe de resgate”: cada um tem uma função clara, mas todos dependem uns dos outros para o sistema sobreviver.

---

### **Estrutura real de uma tarefa – Exemplo (FreeRTOS)**

O kernel representa cada tarefa por meio de uma estrutura de controle — o famoso **TCB (Task Control Block)**.

A versão reduzida a seguir é inspirada diretamente no FreeRTOS:

```c
typedef struct tskTaskControlBlock
{
    volatile StackType_t *pxTopOfStack;   // Contexto salvo
    ListItem_t xStateListItem;            // Estado/prontidão
    UBaseType_t uxPriority;               // Prioridade
    StackType_t *pxStack;                 // Início da stack
    char pcTaskName[ configMAX_TASK_NAME_LEN ]; // Nome da tarefa

} TCB_t;
```

Repare como o TCB é *espartano*: apenas o que o kernel realmente precisa para tomar decisões rápidas. Não há memória virtual, descritores de arquivo ou buffers de I/O complexos. O foco é a **previsibilidade**.

---

### **Criando uma tarefa — exemplo no estilo O’Reilly**

Em FreeRTOS:

```c
void vBlinkTask(void *pvParameters)
{
    for(;;) {
        toggle_led();
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

xTaskCreate(vBlinkTask,
            "Blink",
            128,
            NULL,
            tskIDLE_PRIORITY + 1,
            NULL);
```

Esse exemplo é simples, mas contém um elemento crítico para um RTOS:
`vTaskDelay()` **bloqueia a tarefa**, permitindo que o escalonador ofereça CPU a outras atividades.

---

## **4.2 Ciclo de vida de uma tarefa**

Embora simplificado, o ciclo de vida de uma tarefa em sistemas embarcados é guiado por alguns estados clássicos. Tanenbaum adoraria um diagrama aqui, mas vamos descrevê-lo narrativamente.

### **Estados típicos de uma tarefa em um RTOS**

1. **Ready (Pronta)**
   A tarefa está pronta para ser executada.
   Se for a de maior prioridade disponível, roda imediatamente.

2. **Running (Executando)**
   A tarefa possui o processador.

3. **Blocked (Bloqueada)**
   A tarefa espera algum evento:

   * término de um delay,
   * chegada de dados em uma fila,
   * liberação de um mutex,
   * sinalização de uma ISR.

4. **Suspended (Suspensa)**
   Retirada voluntariamente da lista de prontas (geralmente por API).
   Não participa do escalonamento até ser reativada.

5. **Deleted (Removida)**
   A tarefa foi destruída e sua stack liberada.

---

### **Exemplo prático: transições reais usando FreeRTOS**

```c
void vTaskExample(void *pv)
{
    for(;;) {
        vTaskDelay(1000);       // Running → Blocked
        process_data();         // Blocked → Ready → Running
    }
}
```

Transições:

* Ao chamar `vTaskDelay()`, a tarefa entra no estado **Blocked**.
* Quando o temporizador expira, ela volta a **Ready**.
* Se é a de maior prioridade, o kernel faz o *context switch* e retorna a **Running**.

---

### **Exemplo com evento via ISR (estilo O’Reilly)**

```c
void EXTI0_IRQHandler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    xSemaphoreGiveFromISR(xButtonSem, &xHigherPriorityTaskWoken);

    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

Aqui:

* A ISR desbloqueia uma tarefa pendente em `xButtonSem`.
* Caso essa tarefa tenha prioridade maior que a tarefa atual,
  **o kernel troca de contexto imediatamente ao final da ISR**.

Este mecanismo é absolutamente essencial em sistemas de tempo real: eventos externos **podem promover tarefas instantaneamente**.

---

## **4.3 Context Switching (troca de contexto)**

Se tarefas são personagens de uma história, o *context switch* é a técnica narrativa que permite alternar entre elas sem perder o fio da trama. Em termos técnicos:

> Troca de contexto é o processo de **salvar o estado da tarefa atual** (registradores, ponteiros, stack) e **restaurar o estado de outra**.

Em sistemas embarcados, isso ocorre com frequência e deve ser:

* **rápido**,
* **previsível**,
* e idealmente **constante em tempo** (O(1)).

---

## **Como ocorre a troca de contexto na prática?**

Em praticamente todos os kernels embarcados:

1. O *tick* ou uma ISR dispara o scheduler.
2. O kernel decide qual tarefa deve executar.
3. O contexto da tarefa atual é salvo na sua stack.
4. O contexto da próxima tarefa é restaurado.
5. O processador retorna da interrupção já na nova tarefa.

---

### **Exemplo real (ARM Cortex-M): salvamento automático de contexto**

Uma característica elegante dos Cortex-M é que **parte do contexto é salva automaticamente pelo hardware**, durante uma interrupção.

Quando uma exceção ocorre, o hardware empilha:

* R0–R3
* R12
* LR
* PC
* xPSR

Isso simplifica tremenamente o código do kernel.

Trecho real de assembly reduzido do FreeRTOS (Cortex-M3/M4):

```asm
PendSV_Handler:
    MRS r0, psp                   ; Carrega ponteiro da stack da tarefa atual
    CBZ r0, pendsv_exit           ; Se for a primeira vez, nada a salvar

    ; Salva registradores R4-R11 (não salvos pelo hardware)
    STMDB r0!, {r4-r11}

    ; Salva SP da tarefa atual no TCB
    LDR r1, =pxCurrentTCB
    LDR r1, [r1]
    STR r0, [r1]

    ; Chama scheduler em C
    BL vTaskSwitchContext

    ; Restaura SP da tarefa escolhida
    LDR r1, =pxCurrentTCB
    LDR r1, [r1]
    LDR r0, [r1]

    ; Restaura R4-R11
    LDMIA r0!, {r4-r11}

pendsv_exit:
    MSR psp, r0
    ORR lr, lr, #0x04
    BX lr
```

Esse fragmento é um prato cheio para quem gosta de entender “por baixo do capô” – e um ótimo exemplo do equilíbrio entre software e hardware que um RTOS precisa manter.

---

### **Porque a troca de contexto é crítica**

A troca de contexto é fundamental para:

* multitarefa preemptiva,
* escalonamento por prioridade,
* resposta a interrupções,
* bloqueio e desbloqueio via IPC.

Mas também tem armadilhas:

* custo de tempo variável (em arquiteturas complexas),
* poluição de cache (em MCUs com cache),
* risco de prioridade invertida se não acompanhado de IPC correto.

É por isso que designers de RTOS dedicam tanta atenção à simplicidade do TCB e à previsibilidade do scheduler.

---

# **Capítulo 4 — Gerenciamento de Processos e Tarefas**

## **4.4 Prioridades e Classes de Tarefas**

Se há um elemento que distingue um sistema operacional embarcado de um sistema operacional tradicional, certamente é a **prioridade das tarefas**.
Em um laptop, o navegador pode esperar meio segundo enquanto o sistema recompõe uma janela. Já em uma ECU automotiva, esperar meio segundo pode significar *perder a leitura de um sensor crítico e danificar o motor*. Em outras palavras: **nem todas as tarefas nascem iguais**.

Em um **RTOS típico**, cada tarefa possui dois atributos fundamentais:

1. **Prioridade estática** — definida pelo desenvolvedor e usada para decisões de escalonamento.
2. **Estado atual** — pronto, bloqueado, executando, suspenso, etc.

### ● Prioridades Fixas e Preemptividade

A maioria dos RTOS utiliza **prioridades fixas e preemptivas**.
Isso significa que:

* uma tarefa de prioridade alta *sempre* interrompe uma tarefa de prioridade menor;
* a troca de contexto pode acontecer a qualquer momento em que a tarefa de maior prioridade estiver pronta.

Um trecho reduzido de código real do **FreeRTOS**, usado para criação de tarefas, ilustra isso:

```c
// FreeRTOS: xTaskCreate
BaseType_t xTaskCreate(
    TaskFunction_t pxTaskCode,
    const char * const pcName,
    uint16_t usStackDepth,
    void *pvParameters,
    UBaseType_t uxPriority,   // <- aqui definimos a prioridade da tarefa
    TaskHandle_t *pxCreatedTask
);
```

Um programador desavisado tende a colocar “prioridade alta” em tudo, assim como novatos em banco de dados criam 100 índices “para otimizar”.
O resultado é o caos: tarefas realmente importantes competem com tarefas irrelevantes, e o sistema passa mais tempo trocando contexto do que produzindo trabalho útil.

### ● Classes de Tarefas

É comum dividir tarefas em **classes funcionais**, que orientam o uso de prioridade:

| Classe                        | Exemplo                          | Prioridade típica | Observações                           |
| ----------------------------- | -------------------------------- | ----------------- | ------------------------------------- |
| **Crítica de tempo real**     | Controle de motor, PWM, laço PID | Muito alta        | Não podem perder deadlines            |
| **Alta prioridade funcional** | Comunicação CAN, Ethernet        | Alta              | Podem ter buffers e filas             |
| **Serviços do sistema**       | Logger, tarefas de manutenção    | Média             | Suportam alguma latência              |
| **Tarefas de fundo**          | Telemetria, diagnósticos         | Baixa             | Executam quando o sistema está ocioso |

Em sistemas POSIX embarcados, há classes similares, como **SCHED_FIFO** e **SCHED_RR** (round-robin), usadas via `sched_setscheduler()` no Linux.

---

## **4.5 Problemas Clássicos: Inversão de Prioridade e Starvation**

A teoria é clara: tarefas mais importantes têm prioridade maior.
A prática, porém, é cheia de armadilhas — e a maior delas é a **inversão de prioridade**.

### ● Inversão de Prioridade

Suponha três tarefas:

* **T1** — baixa prioridade
* **T2** — média prioridade
* **T3** — alta prioridade

Agora imagine que T1 e T3 precisam do mesmo mutex.
T1 o adquire primeiro.
Em seguida, T3 tenta adquiri-lo — mas fica **bloqueada**, esperando que T1 o devolva.

O problema é que T2, que não depende do mutex, tem prioridade intermediária. Ela *preempte* T1 infinitamente, impedindo que T1 libere o mutex e desbloqueie T3.
Resultado: **T3 não executa, mesmo sendo a mais importante**.

Sistemas sérios implementam **herança de prioridade (priority inheritance)**.
Nessa técnica, quando T3 bloqueia em um mutex que T1 segura, T1 **temporariamente herda a prioridade de T3**, permitindo que ela execute rapidamente e libere o mutex.

Um trecho real reduzido do **mutex do FreeRTOS**:

```c
// FreeRTOS: Priority inheritance em xQueueTakeMutexRecursive
if (pxMutexHolder->uxPriority < pxCurrentTCB->uxPriority) {
    vTaskPriorityInherit(pxMutexHolder);
}
```

Essa mesma solução é usada no **Linux**, em mutexes do tipo **pi_mutex**.

### ● Starvation

Outro clássico é o *starvation*: tarefas de baixa prioridade **nunca recebem CPU**.
Isso ocorre quando:

* há tarefas de alta prioridade sempre prontas;
* o escalonador não implementa nenhum mecanismo de envelhecimento (*aging*).

RTOS minimalistas frequentemente sofrem desse problema, pois priorizam simplicidade e determinismo.

---

## **4.6 Comunicação e Sincronização entre Tarefas**

Em um sistema embarcado, as tarefas raramente operam isoladas; elas precisam se comunicar.
A questão não é apenas *como*, mas também *quando*.
Se duas tarefas acessam um mesmo sensor, ou compartilham um buffer, é essencial evitar condições de corrida.

Os mecanismos clássicos incluem:

### ● Filas / Queues (RTOS)

Filas são o método mais utilizado em FreeRTOS e Zephyr.
A ideia é simples: **uma tarefa envia mensagens, outra consome**, e o RTOS cuida da sincronização.

```c
// FreeRTOS: enviando dados para uma fila
int temp = read_sensor();
xQueueSend(queueHandle, &temp, portMAX_DELAY);
```

Isso evita o compartilhamento de variáveis globais e reduz o risco de race conditions.

### ● Mutexes

Úteis para controlar acesso exclusivo a regiões críticas.
No entanto, introduzem risco de **inversão de prioridade**, como discutido antes.

### ● Semáforos

São um pouco mais primitivos.
Apesar de extremamente úteis, semáforos são, na prática, fáceis de usar errado — até Tanenbaum sugere cautela:

> “Semáforos são poderosos, mas também são um convite direto a deadlocks se usados sem uma política clara.”

Exemplo FreeRTOS:

```c
xSemaphoreTake(xBinarySemaphore, portMAX_DELAY);
critical_section();
xSemaphoreGive(xBinarySemaphore);
```

### ● Eventos / Event Groups

Permitem que várias flags sejam sinalizadas simultaneamente.
Eficientes, porém específicos de RTOS (não existem em POSIX puro).

### ● Memória Compartilhada (Sistemas maiores)

Em Linux embarcado, é comum usar **mmap()**, **shmget()** ou **pipes**, dependendo da latência e banda necessárias.

---

## **4.7 Criação e Destruição de Tarefas**

Criar uma tarefa em um RTOS não é tão trivial quanto chamar `pthread_create()` em Linux.
Em sistemas embarcados, cada tarefa deve ter:

* sua própria *stack*;
* blocos de controle (TCB);
* prioridade atribuída;
* e, idealmente, consumo de CPU previsível.

### ● Criando uma tarefa (FreeRTOS)

```c
void vSensorTask(void *pvParameters) {
    for(;;) {
        read_sensor();
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

xTaskCreate(
    vSensorTask,
    "Sensor",
    256,         // stack em palavras, não bytes
    NULL,
    3,           // prioridade
    NULL
);
```

### ● Destruição de tarefas

RTOS diferem bastante aqui.
O FreeRTOS permite `vTaskDelete()`, mas muitos RTOS seguem a filosofia “*tarefas não morrem*”.
Elas são suspensas ou entram em estado inativo — útil para reduzir fragmentação de memória e comportamentos imprevisíveis.

```c
// FreeRTOS: deletando a própria tarefa
vTaskDelete(NULL);
```

### ● No Linux

No Linux embarcado:

* criação é feita via `clone()` ou `pthread_create()`;
* destruição é automática quando a thread retorna.

O kernel lida com o gerenciamento completo do *task struct*.

