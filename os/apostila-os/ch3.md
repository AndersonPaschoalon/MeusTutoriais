# **Capítulo 3 — Estrutura de um Sistema Operacional Embarcado**


## **3.1 Funções básicas de um Sistema Operacional**

Ao longo da história da computação, o sistema operacional foi ganhando responsabilidades — de um simples carregador de programas a uma complexa entidade que coordena processadores, memórias e dispositivos.
Nos sistemas embarcados, porém, o sistema operacional vive numa realidade distinta: ele deve ser **leve**, **determinístico**, **modular** e, acima de tudo, **previsível**.

O propósito essencial permanece o mesmo: **permitir que múltiplos componentes de software convivam ordenadamente sobre o mesmo hardware**, evitando o caos absoluto que resultaria se cada módulo tentasse acessar a CPU ou os periféricos de forma descoordenada.

Este papel pode ser dividido em quatro funções básicas:

---

### **3.1.1 Gerenciamento de Processos e Tarefas**

Talvez o papel mais visível de um sistema operacional é decidir **quem usa a CPU** e **quando**.
Em um PC, isso é conhecido como *gerenciamento de processos*.
Em sistemas embarcados, a unidade de execução é mais frequentemente uma **tarefa** (*task*, *thread*), muito mais leve que um processo tradicional.

A função do OS é realizar **escalonamento** (scheduling), definindo qual tarefa deve ser executada.

Exemplo minimalista de criação de tarefa em **FreeRTOS**:

```c
// Exemplo FreeRTOS - criação de duas tarefas
void vSensorTask(void *pvParameters) {
    for (;;) {
        ler_sensor();
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void vComunicacaoTask(void *pvParameters) {
    for (;;) {
        enviar_dados();
    }
}

int main(void) {
    xTaskCreate(vSensorTask, "Sensor", 256, NULL, 2, NULL);
    xTaskCreate(vComunicacaoTask, "Com", 256, NULL, 1, NULL);

    vTaskStartScheduler(); // kernel assume o controle
    for(;;);
}
```

Observe aqui a ideia central: **tarefas coexistem**.
O sistema operacional é quem “segura a batuta”, escolhendo qual tarefa executa a cada instante.

---

### **3.1.2 Gerenciamento de Memória**

Em sistemas embarcados simples, o gerenciamento de memória é quase inexistente: memória fixa, sem paginação, sem swap, e alocação muitas vezes estática.

Porém, sistemas mais complexos — como rodando Linux embarcado — suportam:

* **MMU** (Memory Management Unit)
* **paginação**
* **proteção de memória**
* **isolamento de processos**

Exemplo de alocação em kernel Linux (API do kernel, não libc):

```c
// Kernel Linux - alocação de memória no espaço do kernel
void *buf = kmalloc(1024, GFP_KERNEL);
if (!buf) return -ENOMEM;
// ...
kfree(buf);
```

O uso de *flags* como `GFP_KERNEL` instrui o kernel sobre o contexto da alocação — conceito bastante distinto do mundo do usuário.

---

### **3.1.3 Gerenciamento de Periféricos (Drivers)**

O sistema operacional deve oferecer **uma interface consistente** para acessar dispositivos, abstraindo detalhes de hardware.

Em Linux, o acesso a um LED no sysfs pode ser feito via:

```bash
echo 1 > /sys/class/leds/beaglebone:green:usr0/brightness
```

Em um sistema embarcado com MCU, acessar GPIO pode ser tão simples quanto:

```c
// Exemplo STM32 bare-metal
GPIOA->ODR |= (1 << 5);   // seta PA5
GPIOA->ODR &= ~(1 << 5); // limpa PA5
```

Aqui começa a surgir uma diferença fundamental entre sistemas embarcados:
**com osciladores, GPIOs, ADCs e timers integrados ao chip, o OS precisa conhecer o hardware íntima e profundamente.**

---

### **3.1.4 Comunicação e Sincronização**

Por fim, o OS deve coordenar o acesso a recursos compartilhados.
Sem isso, duas tarefas simultâneas poderiam modificar a mesma variável, gerando resultados imprevisíveis — o que Tanenbaum chamaria de “virtude cardeal da sincronização”.

FreeRTOS utiliza semáforos e filas:

```c
xSemaphoreTake(xMutex, portMAX_DELAY);
acessar_recurso_compartilhado();
xSemaphoreGive(xMutex);
```

No kernel Linux, recursos são protegidos com *spinlocks*:

```c
spinlock_t lock;

spin_lock(&lock);
critical_section();
spin_unlock(&lock);
```

Sincronização é um tema profundo; sua ausência, porém, costuma ser fatal.

---

## **3.2 Núcleo (Kernel) e Camadas do Sistema**

Se imaginarmos o sistema operacional como uma cidade, o kernel seria sua prefeitura: não executa todas as tarefas, mas coordena tudo.

A estrutura típica pode ser dividida em camadas:

---

### **3.2.1 Camada de Hardware**

O nível mais baixo contém CPU, memória, barramentos e periféricos.
É a base física; nada funciona abaixo disso.

---

### **3.2.2 HAL (Hardware Abstraction Layer)**

A HAL é um conjunto de rotinas escritas para abstrair detalhes do hardware.

Exemplo simplificado de HAL para GPIO:

```c
void hal_gpio_write(uint8_t pin, uint8_t val) {
    if (val)
        GPIOA->ODR |= (1 << pin);
    else
        GPIOA->ODR &= ~(1 << pin);
}
```

Ela oferece uma visão unificada, mesmo quando o hardware muda.

---

### **3.2.3 Drivers**

Os drivers vivem acima da HAL.
Um driver de UART, por exemplo, traduz eventos de hardware em operações de leitura e escrita.

Em Linux, o driver expõe uma API padrão:

```c
static ssize_t uart_read(struct file *filp, char __user *buffer,
                         size_t len, loff_t *offset) {
    // transfere dados do driver para o espaço do usuário
}
```

---

### **3.2.4 Kernel (núcleo)**

O kernel é o coração do sistema operacional.
Ele fornece:

* escalonamento
* interrupções
* temporizadores
* IPC (comunicação interprocesso)
* sincronização
* gerenciamento básico de memória

No Cortex-M, a troca de contexto (particularmente didática) pode ser demonstrada em assembly:

```asm
// Cortex-M - parte de uma rotina de troca de contexto (simplificada)
PUSH {r4-r11}        ; salva registradores do contexto da tarefa
LDR r0, =pxCurrentTCB
STR sp, [r0]         ; salva SP da tarefa atual
BL  vTaskSwitch      ; escolhe nova tarefa
LDR r0, =pxCurrentTCB
LDR sp, [r0]         ; restaura SP
POP {r4-r11}         ; restaura registradores
BX LR
```

Esse trecho mostra, de forma crua, o que o kernel de um RTOS realmente faz:
**congelar uma tarefa, descongelar outra e continuar como se nada tivesse acontecido.**

---

### **3.2.5 Aplicações**

Por fim, no topo da pirâmide, estão as aplicações — que podem ser:

* tarefas em RTOS,
* processos em Linux,
* máquinas de estado em sistemas bare-metal.

O sistema operacional é o intermediário que permite a essas aplicações coexistirem sem interferência destrutiva.

---

## **3.3 Kernel Monolítico, Microkernel e Híbrido**

Assim como há diferentes filosofias políticas para governar uma cidade, também há diferentes filosofias para estruturar um kernel.
Tanenbaum discute isso extensivamente (e ironicamente, parte disso motivou debates acalorados com Linus Torvalds ao longo dos anos).

Existem três modelos principais:

---

### **3.3.1 Kernel Monolítico**

No modelo monolítico, **o kernel contém tudo**:
drivers, gerenciamento de memória, sistemas de arquivos, pilhas de rede, etc.

**Exemplos:**

* Linux
* BSD
* Zephyr (parcialmente modular, mas essencialmente monolítico)

A grande vantagem é o **desempenho**: todas as funções estão no mesmo espaço de memória, sem chamadas de IPC custosas.

A desvantagem: **uma falha em um driver pode derrubar o sistema inteiro**.

---

### **3.3.2 Microkernel**

O microkernel adota a filosofia oposta:
**o kernel deve conter apenas o mínimo absolutamente essencial** — escalonamento, IPC, interrupções.

Todo o resto (drivers, sistemas de arquivos, etc.) roda em **modo usuário**, como serviços isolados.

**Exemplos:**

* MINIX 3 (criado por Tanenbaum)
* QNX
* seL4

Chamada de IPC em Minix (exemplo O’Reilly-style):

```c
// processo envia mensagem ao driver
message m;
m.type = DEV_READ;
send(driver_pid, &m);

// aguarda resposta
receive(driver_pid, &m);
```

A filosofia é clara:
**se um driver falha, ele morre — mas o sistema continua vivo.**

---

### **3.3.3 Kernel Híbrido**

Kernel híbrido é um termo meio nebuloso, usado para descrever sistemas que ficam entre os dois extremos.

**Exemplos típicos:**

* Windows NT
* XNU (macOS)
* algumas variantes de RTOS comerciais

A ideia é mesclar:

* arquitetura modular,
* desempenho semelhante ao monolítico,
* alguma proteção e isolamento.

---

#### **Resumo visual dos modelos**

```
Monolítico:    [ TUDO dentro do kernel ]
Microkernel:   [ kernel pequeno ] + [ drivers em user-space ]
Híbrido:       [ kernel grande, modular ] mas não completamente monolítico
```

A seguir está a **continuação do Capítulo 3**, seguindo rigorosamente:

* o **estilo narrativo e didático de Tanenbaum**,
* exemplos práticos no estilo **O’Reilly**,
* trechos reais de **C/assembly**, comentados e contextualizados,
* coerência com o conteúdo já escrito.

---

## **3.4 Chamadas de Sistema e Modo Supervisor**

Ao longo da história dos sistemas operacionais, descobriu-se que permitir ao software de usuário controlar diretamente o hardware era um convite ao caos. Uma única instrução errada poderia travar o processador ou sobrescrever regiões críticas da memória. Como solução, arquiteturas modernas introduziram **níveis de privilégio**, normalmente ao menos dois:

* **Modo usuário (User Mode)**: permissões limitadas.
* **Modo supervisor (Kernel Mode)**: acesso total ao hardware.

Em sistemas embarcados, os nomes variam — ARM Cortex-M fala em *privileged* e *unprivileged* —, mas a ideia permanece: algumas instruções só podem ser executadas pelo **kernel**, e o caminho oficial para o mundo privilegiado passa pelas **system calls**.

#### **A chamada de sistema como “fronteira segura”**

Uma *system call* é, essencialmente, uma **solicitação formal** para que o kernel execute uma operação privilegiada em nome de uma tarefa. Isso se dá por meio de uma instrução especial — em ARM Cortex-M, a conhecida **SVC (Supervisor Call)** — que:

1. **interrompe a execução normal**,
2. **salta para um vetor especial de interrupção**,
3. **executa a função solicitada**.

#### **Exemplo Real (ARM Cortex-M): Uma system call mínima**

No código abaixo (estilo O’Reilly: curto, claro e comentado), temos o esqueleto de uma *system call* customizada utilizando a instrução **SVC**:

#### **Assembly — Chamando um serviço do kernel**

```asm
; Arquivo: call_service.s
; Executa uma chamada de sistema com código de serviço armazenado em R0

.global call_service
call_service:
    SVC #0      ; Gatilho para o modo supervisor
    BX LR
```

#### **C — Handler de SVC (baseado em ARMv7-M, estilo FreeRTOS)**

```c
void SVC_Handler(void)
{
    uint32_t svc_number;

    /* Obtém o valor da pilha contendo a instrução SVC */
    uint32_t *stacked_pc = (uint32_t*)__get_PSP();
    uint16_t instruction = *((uint16_t*)(stacked_pc - 1));

    /* Extrai o número da SVC (baixos 8 bits) */
    svc_number = instruction & 0xFF;

    switch(svc_number) {
        case 0:
            kernel_do_something();
            break;

        default:
            kernel_panic("SVC desconhecida!");
    }
}
```

Aqui observamos algo típico de sistemas embarcados: o kernel não é grande e genérico como no Linux, mas pequeno e especializado. Analisar manualmente a instrução SVC é comum, pois reduz overhead e aumenta previsibilidade.

#### **Por que isso importa no embarcado?**

* **Segurança mínima mesmo em hardware sem MMU**
  A MPU (quando existe) protege regiões, mas ainda dependemos do modo privilegiado para evitar que tarefas sobrescrevam registradores dos periféricos.

* **Interface estável entre aplicação e kernel**
  A API do RTOS é implementada como chamadas de sistema — por exemplo, `vTaskDelay()` e `xQueueSend()` no FreeRTOS.

* **Base do determinismo**
  Um kernel só pode ser determinístico se **controlar completamente** as operações privilegiadas.

---

## **3.5 Estrutura do RTOS (FreeRTOS, Zephyr, etc.)**

Um RTOS (Real-Time Operating System) é desenhado não para maximizar throughput, mas sim para maximizar **previsibilidade** e **latência controlada**. Tanenbaum enfatizaria que a prioridade não é “fazer o máximo de trabalho possível”, e sim “fazer o trabalho certo no tempo certo”.

Apesar de diferenças de implementação, a arquitetura interna de um RTOS costuma seguir um padrão bastante claro.

---

#### **Componentes essenciais de um RTOS típico**

1. **Scheduler de tempo real**
   Decide qual tarefa executar de acordo com prioridades e política (preemptiva, Round Robin, Rate Monotonic etc.).

2. **Gerenciamento de tarefas**
   Estruturas de controle (TCB – Task Control Block) contendo:

   * ponteiro de stack,
   * prioridade,
   * estado (ready, running, blocked, suspended),
   * lista de recursos.

3. **IPC — Comunicação entre tarefas**
   Filas (queues), semáforos, mutexes, eventos.

4. **Sistema de temporização**
   Baseado no *tick* (regular) ou *tickless* (event-driven).

5. **Gerenciamento de interrupções**
   Integração clara entre ISRs e tarefas (deferimento, notificações, etc.).

6. **Drivers e HAL**
   Independência parcial de hardware, especialmente no Zephyr.

---

#### **Exemplo Real: Estrutura interna do FreeRTOS**

O FreeRTOS é provavelmente o RTOS mais difundido no mundo microcontrolado. Sua arquitetura é tão elegante quanto minimalista.

#### **TCB simplificado do FreeRTOS (extraído e reduzido)**

```c
typedef struct tskTaskControlBlock
{
    volatile StackType_t *pxTopOfStack;

    ListItem_t xStateListItem;
    ListItem_t xEventListItem;

    UBaseType_t uxPriority;
    StackType_t *pxStack;

    char pcTaskName[ configMAX_TASK_NAME_LEN ];

} TCB_t;
```

Observações didáticas (estilo Tanenbaum):

* Não encontramos estruturas rebuscadas ou genéricas: apenas o **essencial**.
* O kernel evita abstrações complexas para manter a previsibilidade.
* Quase tudo é manipulável por listas encadeadas, o que facilita análise de pior caso.

---

#### **Estrutura do Zephyr**

O Zephyr segue uma abordagem mais moderna e modular, suportando:

* *device tree* (como no Linux),
* APIs padronizadas para drivers,
* suporte multiprocessador (SMP),
* thread-aware power management.

O Zephyr é, em certo sentido, um “mini Linux embarcado”, mas com custo de execução muito menor.

---

## **3.6 O Papel do Scheduler e do Tick System**

Se o kernel é o cérebro de um RTOS, então o **scheduler** é o seu lobo frontal — a parte responsável por decidir *quem* merece atenção e *quando*. Já o **tick system** é o sistema de temporização, fornecendo o “ritmo cardíaco” para decisões temporais.

#### **Como o kernel decide qual tarefa executar**

O *scheduler* mantém listas de tarefas prontas separadas por prioridade. Em muitos RTOS (como FreeRTOS), as listas são:

* **Array de listas**, uma por prioridade,
* onde o scheduler sempre escolhe **o primeiro item da lista de maior prioridade não vazia**.

Este design permite escalonamento O(1), crucial para sistemas de tempo real.

---

#### **O Tick Timer como Metronomo do Kernel**

Tradicionalmente, RTOS operam com um **tick periódico**, vindo por exemplo do SysTick:

* cada interrupção do tick incrementa o tempo global,
* decrementa temporizadores pendentes,
* e acorda tarefas que estavam bloqueadas com timeout.

#### **Exemplo de handler do SysTick (FreeRTOS-like)**

```c
void SysTick_Handler(void)
{
    // Atualiza o contador de tempo
    xTaskIncrementTick();

    // Decide se devemos realizar um reschedule
    if ( xNeedReschedule() )
        vTaskSwitchContext();
}
```

Observe o padrão:

1. O tick ocorre em **interrupção**,
2. e ao final dela o kernel **pode trocar de contexto**.

---

#### **Tickless RTOS: quando o sistema dorme profundamente**

Sistemas que precisam economizar energia (sensores IoT, medidores inteligentes, wearables) não podem se dar ao luxo de acordar centenas de vezes por segundo.

O modo **tickless** elimina o tick periódico:

* o RTOS programa um timer para acordar **somente quando necessário**,
* reduzindo drasticamente consumo.

Exemplo simplificado:

```
sleep_until(next_timeout);
```

O kernel acorda apenas para eventos reais, não para manter um relógio arbitrário.

---

