# 📘 **Capítulo 5 — Escalonamento e Tempo Real**

Se nos capítulos anteriores discutimos o mecanismo pelo qual um sistema operacional embarcado *gerencia*, *cria*, *sincroniza* e *substitui* tarefas, agora finalmente entramos no coração do que diferencia um sistema embarcado comum de um **sistema embarcado de tempo real**. É aqui que conceitos como “prazo”, “determinismo”, “latência” e “preempção” deixam de ser abstrações e se tornam mecanismos concretos que definem se um robô desvia de um obstáculo a tempo — ou não.

Como diria Tanenbaum, “sistemas operacionais não servem apenas para manter o computador ocupado; eles servem para evitar desastres”. Em um ambiente embarcado, essa frase assume um peso literal.

---

# **5.1 — Conceitos de Tempo Real (Hard e Soft Real-Time)**

A primeira coisa a compreender é que **tempo real não significa ‘rápido’**, e sim **previsível**. Há sistemas extremamente rápidos que não são de tempo real, e sistemas relativamente lentos que são. A questão central é: *o sistema garante que uma tarefa será executada dentro de um limite de tempo conhecido?*

Para formalizar isso, a literatura costuma separar sistemas de tempo real em duas classes principais:

---

## **5.1.1 — Hard Real-Time**

Um sistema é chamado de **hard real-time** quando **perder um prazo é inaceitável**.
Inaceitável pode significar:

* queimar um componente,
* causar um acidente físico,
* violar um contrato legal ou industrial,
* corromper um processo de produção.

Exemplos típicos incluem:

* controle de motor em E/S industriais,
* airbags automotivos,
* controle de voo,
* equipamentos médicos.

Uma tarefa de hard real-time geralmente é especificada com:

* uma **deadline absoluta**:
  “deve rodar a cada 1 ms, com jitter inferior a 5 μs”;
* um **pior tempo de execução conhecido** (*Worst-Case Execution Time*, WCET);
* um **pior tempo de resposta esperado** (*Worst-Case Response Time*, WCRT).

---

## **5.1.2 — Soft Real-Time**

Soft real-time é menos rigoroso. Aqui **perder uma deadline é indesejável, mas não catastrófico**.

Exemplos:

* áudio e vídeo (ocasionais quedas podem ser toleradas),
* streaming,
* sensores ambientais,
* monitoramento IoT não-crítico.

O foco em soft RT está em:

* manter a fluidez,
* reduzir jitter,
* manter média de tempo de resposta baixa,
* evitar congestionamento entre tarefas.

---

## **5.1.3 — Firm Real-Time (categoria intermediária)**

Alguns autores incluem uma categoria intermediária chamada **firm real-time**, onde:

* perder uma deadline invalida o resultado,
* mas o sistema continua funcional.

Por exemplo:
Um pacote de dados que chega atrasado demais para ser útil pode simplesmente ser descartado.

---

## **Ilustração simples**

Se uma tarefa deve executar a cada 10 ms e ela atrasar:

* **hard RT:**
  o sistema está *errado* (e pode ser perigoso).

* **soft RT:**
  o sistema está *incorreto*, mas tolerável.

* **firm RT:**
  o resultado dessa instância é inútil, mas o sistema segue funcionando.

---

# **5.2 — Determinismo e Latência**

Determinismo é a *palavra mágica* dos sistemas de tempo real.
Muito mais importante que **quem** é escalonado, é **quando** ele *será* escalonado — e com quanto de variação.

---

## **5.2.1 — Determinismo**

Um sistema é determinístico quando:

* o tempo entre eventos é previsível,
* a variação (jitter) é mínima,
* o pior caso é conhecido.

Por exemplo, considere o tempo entre uma interrupção de timer e a execução da rotina que processa essa interrupção.
Se o tempo varia entre **80 μs** e **95 μs**, ele é bastante determinístico.
Se varia entre **80 μs** e **2300 μs**, mesmo que a média seja boa, o sistema é **não determinístico** — e provavelmente inadequado para tempo real rigoroso.

---

## **5.2.2 — Latência**

Latência é o *atraso* entre:

* a ocorrência de um evento, e
* o início da ação correspondente.

Em tempo real, falamos de vários tipos:

* **latência de interrupção:**
  tempo entre hardware -> CPU -> ISR;
* **latência de escalonamento:**
  tempo entre uma tarefa se tornar elegível e de fato executar;
* **latência de resposta total:**
  a soma de todos os atrasos.

Em Linux, por exemplo, mede-se latência de interrupção com ferramentas como `cyclictest` (muito conhecida no contexto PREEMPT_RT).
Em sistemas bare-metal, o mesmo pode ser medido configurando-se um GPIO no início da ISR e monitorando com um osciloscópio.

---

## **Exemplo real: medindo latência em um STM32 (bare-metal)**

```c
// Exemplo didático: mede o tempo entre o estouro de um timer e o início da ISR.
// Plataforma: STM32F4 (ARM Cortex-M4)

void TIM2_IRQHandler(void) {
    GPIOA->ODR ^= (1 << 5);   // toggle rápido para medir no osciloscópio
    TIM2->SR &= ~1;           // limpa flag
}
```

Ao observar o pino PA5 no osciloscópio, medimos a diferença entre:

* o momento do evento de timer,
* e o início da ISR.

Diferenças de microssegundos revelam se o sistema é determinístico.

---

# **5.3 — Escalonamento Preemptivo e Cooperativo**

No capítulo anterior discutimos criação, vida e morte de tarefas. Agora discutiremos *como* selecionar qual tarefa roda a seguir. Há duas grandes filosofias:

1. **escalonamento cooperativo**, e
2. **escalonamento preemptivo**.

Ambas têm virtudes e defeitos que definem o caráter do sistema operacional.

---

## **5.3.1 — Escalonamento Cooperativo**

Neste modelo, **as tarefas precisam voluntariamente ceder a CPU**.
O kernel jamais interrompe uma tarefa à força; ele confia que cada tarefa fará chamadas como:

* `taskYIELD()` (FreeRTOS),
* `sched_yield()` (POSIX),
* ou retornará naturalmente ao kernel.

### Vantagens:

* Simplicidade: ideal para sistemas pequenos.
* Previsibilidade: nada interrompe uma tarefa no meio.
* Depuração facilitada: não há preempção inesperada.

### Desvantagens:

* Se uma tarefa “esquecer” de devolver a CPU → sistema inteiro trava.
* Latência pode ser muito alta em casos de tarefas mal programadas.
* Ineficiente em sistemas com muitas prioridades.

### Exemplo (pseudo-FreeRTOS cooperativo):

```c
void vTaskSensor(void *p) {
    while (1) {
        ler_sensor();
        processar();
        taskYIELD();   // devolve a CPU manualmente
    }
}
```

Se `ler_sensor()` bloquear por 10 ms, nenhuma outra tarefa roda nesse intervalo.

---

## **5.3.2 — Escalonamento Preemptivo**

Aqui, o kernel **interrompe tarefas a qualquer momento**, com base em:

* prioridades,
* deadlines,
* eventos,
* tick timer.

A preempção é o que dá ao sistema um comportamento previsível — mesmo que isso gere maior complexidade e necessidade de troca de contexto constante.

### Vantagens:

* Permite deadlines rígidas.
* Melhor utilização do processador.
* O kernel controla o sistema, não o programador.

### Desvantagens:

* Complexidade maior (context switching).
* Exige exclusão mútua adequada.
* Pode haver jitter por interrupções concurrentes.

No FreeRTOS, por exemplo, o sistema é “tick-driven”:
um temporizador dispara a cada 1 ms (ou 10 ms), invocando o scheduler.

### Exemplo de preempção no FreeRTOS (ARM, assembly simplificado)

Abaixo está uma versão reduzida da sequência ARM usada para troca de contexto durante uma preempção por SysTick (didática, não completa):

```asm
SysTick_Handler:
    /* Salva contexto da tarefa atual */
    mrs r0, psp
    stmdb r0!, {r4-r11}   ; salva registradores não voláteis
    ldr r1, =pxCurrentTCB
    ldr r1, [r1]
    str r0, [r1]          ; salva stack pointer da tarefa atual

    /* Escolhe próxima tarefa */
    bl vTaskSwitchContext

    /* Restaura contexto da nova tarefa */
    ldr r1, =pxCurrentTCB
    ldr r1, [r1]
    ldr r0, [r1]          ; pega o novo PSP
    ldmia r0!, {r4-r11}   ; restaura registradores
    msr psp, r0

    bx lr
```

Esse pequeno trecho ilustra a mecânica real de um scheduler preemptivo:
ele **interrompe** a tarefa atual e **carrega outra** — de acordo com prioridades.


## **5.4 — Algoritmos de Escalonamento (RR, RM, EDF)**

Ao falar de algoritmos de escalonamento em sistemas embarcados, entramos em um território que Tanenbaum sempre abordava com elegância: o casamento entre teoria matemática e a vida real — onde sensores têm atrasos, motores têm inércia, e, se a tarefa que controla o freio ABS atrasar, o carro não espera pacientemente que o processador “respire”.

Nos sistemas embarcados, especialmente nos de tempo real, o algoritmo de escalonamento não é apenas uma preferencia estética: ele pode determinar se o sistema funciona ou falha. Com isso em mente, vamos analisar os principais algoritmos utilizados em RTOS modernos.

---

### **5.4.1 Round Robin (RR)**

O algoritmo *Round Robin* é quase sempre o primeiro que alguém implementa ao escrever um pequeno OS por curiosidade — e não sem motivo. Ele é simples, justo e funciona bem quando todas as tarefas têm prioridade igual.

O funcionamento é direto:

1. Cada tarefa recebe um *quantum* (intervalo fixo de CPU).
2. Quando o quantum expira, o escalonador remove a tarefa da CPU e passa para a próxima.
3. No final da fila, o processo reinicia.

No FreeRTOS, RR só ocorre entre tarefas de **mesma prioridade**, algo comum em RTOS: prioridade sempre vence quantum.

***Exemplo de pseudo Round Robin (estilo Linux 2.4, simplificado):***

```c
void schedule_rr(void) {
    task_t *current = dequeue_ready_list();
    run(current, QUANTUM);

    if (current->state == RUNNABLE)
        enqueue_ready_list(current);
}
```

RR é adequado quando:

* Todas as tarefas têm carga semelhante
* Não há requisitos rígidos de tempo real
* Buscamos isolamento simples entre tarefas

Ainda assim, RR não fornece garantias temporais fortes — portanto, raramente serve para *hard real-time*.

---

### **5.4.2 Rate Monotonic (RM)** — *o favorito dos puristas do tempo real*

Rate Monotonic é um algoritmo seminal, matematicamente provado por Liu & Layland em 1973, e se tornou uma pedra fundamental do escalonamento determinístico.

A regra é extremamente simples:

> Quanto menor o período da tarefa, maior sua prioridade.

Assim, uma tarefa que roda a cada 1 ms tem prioridade mais alta do que outra que roda a cada 10 ms.

Ele é:

* **Preemptivo**,
* **Estático** (prioridades fixas),
* **Determinístico**,
* Ideal para *hard real-time* desde que certas condições matemáticas sejam satisfeitas.

***Exemplo de tabela de tarefas para RM:***

| Tarefa | Período | Execução | Prioridade |
| ------ | ------- | -------- | ---------- |
| T1     | 1 ms    | 0.1 ms   | Alta       |
| T2     | 10 ms   | 1 ms     | Média      |
| T3     | 50 ms   | 2 ms     | Baixa      |

Os RTOS normalmente deixam explícita essa relação. Por exemplo, no FreeRTOS, basta criar tarefas com prioridades definidas manualmente — o programador implementa RM ao atribuir prioridades conforme o período.

---

### **5.4.3 Earliest Deadline First (EDF)** — *o queridinho dos teóricos*

Se RM é um algoritmo clássico, EDF é o mais poderoso. Ele atribui prioridade dinamicamente:

> A tarefa com o deadline mais próximo recebe a CPU.

O grande mérito do EDF:

* Ele consegue cumprir 100% de utilização da CPU (teoricamente), onde RM se limita a ~69% em sistemas harmônicos.

O problema:

* Ele é mais complexo,
* Requer manipulação constante das filas de tarefas,
* Implementação mais custosa no kernel,
* Nem sempre ideal em microcontroladores mais simples.

Ainda assim, Zephyr, FreeRTOS e outros RTOS modernos possuem implementações ou variantes EDF, ainda que muitas vezes opcionais.

***Exemplo simplificado de cálculo de prioridade EDF:***

```c
void edf_schedule(void) {
    task_t *t = find_task_with_earliest_deadline();
    context_switch_to(t);
}
```

Em resumo:

* **RR** → Simples, mas pouco determinístico
* **RM** → Estático, matematicamente provado, excelente para hard real-time
* **EDF** → Ótimo aproveitamento da CPU, dinâmico, mais complexo

---

## **5.5 — Avaliação de Escalonabilidade**

Tanenbaum adorava esta parte: transformar a CPU em uma entidade meticulosamente contabilizada.

A grande pergunta de tempo real é sempre:
**O sistema consegue cumprir todos os prazos?**

Isso é respondido com *análise de escalonabilidade* (schedulability analysis). Há duas abordagens principais:

---

### **5.5.1 Teste de Utilização — Liu & Layland (para RM)**

A condição clássica:

[
U = \sum_{i=1}^{n} \frac{C_i}{T_i}
]

Onde:

* ( C_i ) = tempo de execução da tarefa
* ( T_i ) = período
* ( U ) = utilização total da CPU

Para que **RM** garanta deadlines:

[
U \le n(2^{1/n} - 1)
]

Para 1 tarefa → 100%
Para 2 tarefas → 83%
Para 3 tarefas → 78%
…
Para n → 69% (aproximado)

---

### **5.5.2 Teste Exato — EDF**

EDF é mais poderoso:

[
U \le 1.0
]

Se a soma dos tempos das tarefas não ultrapassar 100% da CPU, EDF garante prazos — simples assim.

---

### **5.5.3 Análise de interferência e jitter**

Tarefas de maior prioridade interferem em tarefas menores.
Analisar isso envolve:

* Preempções
* Overheads de context switching
* Latências de interrupções (ISR latency)
* Jitter do clock do sistema

Muitos RTOS incluem ferramentas automáticas para medir jitter e latência — Zephyr, por exemplo, tem medidores internos integrados via tracing.

---

## **5.6 — Temporizadores e Interrupções Periódicas**

Nenhum escalonador funciona sem o equivalente ao metrônomo de um músico: **o temporizador do sistema**. Ele é responsável por gerar interrupções periódicas que alimentam o *tick* do kernel.

---

### **5.6.1 O *system tick***

A cada interrupção do *tick*, tipicamente de 1 ms:

1. O contador global incrementa
2. Tarefas atrasadas são acordadas
3. Timeouts são verificados
4. O escalonador decide se deve ocorrer preempção

No FreeRTOS, isso aparece assim:

```c
void xPortSysTickHandler(void)
{
    xPortSysTickHandler();   // Atualiza o RTOS
}
```

Em ARM Cortex-M, o SysTick é padronizado pelo próprio core:

```c
void SysTick_Handler(void) {
    HAL_IncTick();
    osSystickHandler(); // Chamada padrão em muitos RTOS
}
```

---

### **5.6.2 Temporizadores independentes (TIM, GPT, PIT)**

Usados quando:

* O *tick* precisa ser desligado (sistemas *tickless*)
* Temporização precisa de precisão nanométrica
* PWM, medição de frequência, geração de pulsos, periodos longos, etc.

Exemplo de configuração de timer em ARM:

```c
TIM3->PSC = 79;      // Prescaler
TIM3->ARR = 999;     // Auto-reload
TIM3->CR1 |= TIM_CR1_CEN;  // Habilita
```

---

### **5.6.3 Interrupções periódicas e ISR latency**

Uma ISR que demora demais causa:

* *jitter*
* perda de deadlines
* aumento brutal da latência de tarefas
* efeitos catastróficos em hard real-time

RTOS sérios impõem regras como:

* ISR deve ser curtíssima
* Nunca bloquear
* Nunca usar recursos pesados (mutex, fila grande, malloc)
* Preferir *deferred work* no contexto de tarefa

---

## **Encerramento do Capítulo 5**

Com isso, fechamos o capítulo mais “matemático” do livro, onde o relógio passa a ser personagem central do drama embarcado. A partir daqui, entramos em terrenos mais sistêmicos (memória, drivers, sincronização avançada), mas a base conceitual de tempo real já está firmada.

Se quiser, podemos seguir para o **Capítulo 6 — Gerenciamento de Memória**, que também dá muito pano pra manga.
